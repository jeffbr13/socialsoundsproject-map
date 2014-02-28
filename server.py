#!python
# -*- coding: utf-8 -*-
"""Back-end server for socialsoundsproject.com"""
from datetime import datetime
import json
import logging
from os import environ
from urlparse import urlparse

from flask import Flask, render_template, request, jsonify, redirect
import redis
import soundcloud

from models import LOCATIONS, Sound, UploadSoundForm


SERVER_URL = 'http://www.socialsoundsproject.com'
SOUNDCLOUD_CALLBACK_PATH = '/soundcloud/callback'

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
REDIS_CACHE = None
SOUNDCLOUD_CLIENT = None
SOUNDCLOUD_SOUNDS = None


def init_cache(redis_url):
    logging.debug('Connecting to Redis cache...')
    url = urlparse(redis_url)
    return redis.Redis(host=url.hostname, port=url.port, password=url.password)


def init_soundcloud(token_store):
    """
    Returns SoundCloud client to use.
    """
    logging.debug('Initialising SoundCloud client...')
    access_token = token_store.get('soundcloud:access_token')
    if access_token:
        return soundcloud.Client(client_id=environ.get('SOUNDCLOUD_CLIENT_ID'),
                                 client_secret=environ.get('SOUNDCLOUD_CLIENT_SECRET'),
                                 redirect_uri=(SERVER_URL + SOUNDCLOUD_CALLBACK_PATH),
                                 access_token=access_token)
    else:
        return soundcloud.Client(client_id=environ.get('SOUNDCLOUD_CLIENT_ID'),
                                 client_secret=environ.get('SOUNDCLOUD_CLIENT_SECRET'),
                                 redirect_uri=(SERVER_URL + SOUNDCLOUD_CALLBACK_PATH))


def get_sounds(soundcloud_client):
    """
    Get all geolocated Sounds in the authenticated user's stream.
    """
    logging.info(
        'Fetching sound data from {user}\'s SoundCloud stream.'.format(user=soundcloud_client.get('/me').obj.get('username'))
        )
    sounds = []
    try:
        page_size = 50
        offset = 0
        tracks = []
        page = soundcloud_client.get('/me/tracks', limit=page_size)
        while len(page) > 0:
            tracks.extend(page)
            offset += page_size
            page = soundcloud_client.get('/me/tracks', limit=page_size, offset=offset)

        logging.info('Got list of {0} sounds from SoundCloud.'.format(len(tracks)))
    except Exception as e:
        logging.error('Couldn\'t get SoundCloud sounds, try authenticating: {0}'.format(e))
        return

    for track in tracks:
        sound = build_sound(track)
        if sound:
            sounds.append(sound)

    logging.info('Built {0} geolocated sound objects from SoundCloud.'.format(len(sounds)))
    return sounds


def build_sound(soundcloud_track):
    """
    Build a Sound from the track object returned by the SoundCloud API,
    or return None.
    """
    try:
        logging.debug(u'Building sound object: "{0}"'.format(soundcloud_track.obj.get('title')))
        tags = soundcloud_track.obj.get('tag_list').split()
        lats = {float(tag.split(u'=')[1]) for tag in tags if u'geo:lat=' in tag}
        lons = {float(tag.split(u'=')[1]) for tag in tags if u'geo:lon=' in tag}
        human_readable_location = soundcloud_track.obj.get('title')

        if lats and lons:
            sound = Sound(soundcloud_id=soundcloud_track.obj.get('id'),
                          latitude=lats.pop(),
                          longitude=lons.pop(),
                          human_readable_location=human_readable_location,
                          description=soundcloud_track.obj.get('description'))
            logging.debug('Sound successfully processed: "{0}"'.format(sound))
            return sound

    except Exception as e:
        logging.warning(
            'Exception in processing sound "{title}": {exception}'.format(title=soundcloud_track.obj.get('title'),
                                                                          exception=e)
            )
        return None


def check_sounds_refresh():
    """
    Gets sounds again, if the <sounds:refresh> key is set.
    """
    if REDIS_CACHE.get('sounds:refresh'):
        logging.info('<sounds:refresh> key found, refreshing sounds...')
        SOUNDCLOUD_SOUNDS = get_sounds(SOUNDCLOUD_CLIENT)
        REDIS_CACHE.delete('soundcloud:new')
        logging.debug('<sounds:refresh> key unset.')


@app.route('/')
def index():
    """
    Serve the index page.
    """
    return render_template('index.html', locations=LOCATIONS)


@app.route('/soundcloud/authenticate')
def soundcloud_authenticate():
    """
    Authenticate as a SoundCloud user.

    Accessing this URL drops any previous stored session information.
    """
    REDIS_CACHE.delete('soundcloud:access_token')
    REDIS_CACHE.delete('soundcloud:scope')
    SOUNDCLOUD_CLIENT = init_soundcloud(REDIS_CACHE)
    return redirect(SOUNDCLOUD_CLIENT.authorize_url())


@app.route(SOUNDCLOUD_CALLBACK_PATH)
def soundcloud_callback():
    """
    Extract SoundCloud authorisation code.
    """
    code = request.args.get('code')
    access_token = SOUNDCLOUD_CLIENT.exchange_token(code=request.args.get('code'))
    REDIS_CACHE.set('soundcloud:access_token', access_token.access_token)
    REDIS_CACHE.set('soundcloud:scope', access_token.scope)
    return render_template('soundcloud-callback.html', user=SOUNDCLOUD_CLIENT.get('/me'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_sound():
    """
    Serve the 'upload sound' form for GET requests,
    and process the results of a POST request, uploading the sound to SoundCloud.
    """
    form = UploadSoundForm(request.form)
    if request.method == 'POST' and form.validate():
        logging.info('Upload form validated, posting to SoundCloud...')
        track = SOUNDCLOUD_CLIENT.post('/tracks', track={
            'title': u'{location}'.format(location=form.human_readable_location.data),
            'description': form.description.data,
            'asset_data': request.files[form.sound.name],
            'tag_list': 'socialsoundsproject geo:lat={lat} geo:lon={lon}'.format(lat=form.latitude.data, lon=form.longitude.data),
            'track_type': 'recording',
            'license': 'cc-by',
            'downloadable': 'true',
        })
        logging.debug('Sound uploaded, setting <sounds:refresh> key and sending user home.')
        REDIS_CACHE.set('sounds:refresh', True)
        return redirect('/')

    return render_template('upload-sound.html', form=form)


@app.route('/sounds.json')
def all_sounds():
    """
    Return JSON for all sounds.
    """
    check_sounds_refresh()
    return jsonify(sounds=SOUNDCLOUD_SOUNDS)


@app.route('/locations.json')
def locations():
    """
    Return JSON for available projects.
    """
    return jsonify(locations=LOCATIONS)


@app.route('/refresh')
def refresh_sounds():
    """
    Manually refresh sounds.
    """
    REDIS_CACHE.delete('soundcloud:new')
    SOUNDCLOUD_SOUNDS = get_sounds(SOUNDCLOUD_CLIENT)
    return redirect('/')


if __name__ == '__main__':
    logging.info('Starting server...')
    REDIS_CACHE = init_cache(environ.get('REDISCLOUD_URL'))
    SOUNDCLOUD_CLIENT = init_soundcloud(REDIS_CACHE)
    SOUNDCLOUD_SOUNDS = get_sounds(SOUNDCLOUD_CLIENT)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5000))
    logging.debug('Launching Flask app...')
    app.run(host='0.0.0.0', port=port, debug=True)

