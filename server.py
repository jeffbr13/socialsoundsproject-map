#!python
# -*- coding: utf-8 -*-
"""Back-end server for socialsoundsproject.com"""
from datetime import datetime
import logging
from os import environ
from urlparse import urlparse

from flask import Flask, render_template, request, jsonify, redirect
import redis
import soundcloud

from models import Sound, UploadSoundForm


SERVER_URL = 'http://socialsoundsproject.herokuapp.com'
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


def get_sounds(client):
    """
    Get all geolocated Sounds in the authenticated user's stream.
    """
    logging.info(
        'Fetching sound data from {user}\'s SoundCloud stream.'.format(user=client.get('/me').obj.get('username'))
        )
    sounds = []
    try:
        tracks = client.get('/me/tracks')
    except Exception as e:
        logging.error('Couldn\'t get SoundCloud sounds, try authenticating: {0}'.format(e))

    for track in tracks:
        try:
            logging.debug(u'Building sound object: "{0}"'.format(track.obj.get('title')))
            tags = track.obj.get('tag_list').split()
            lats = {float(tag.split('=')[1]) for tag in tags if u'geo:lat=' in tag}
            lons = {float(tag.split('=')[1]) for tag in tags if u'geo:lon=' in tag}
            human_readable_location, date_time_etc = track.obj.get('title').split(', ', 1)
            dttm = datetime.strptime(date_time_etc[:18], '%b %d %Y, %H:%M')

            if lats and lons:
                sound = Sound(soundcloud_id=track.obj.get('id'),
                              latitude=lats.pop(),
                              longitude=lons.pop(),
                              human_readable_location=human_readable_location,
                              description=track.obj.get('description'),
                              datetime=dttm)
                sounds.append(sound)
                logging.debug('Sound successfully processed: "{0}"'.format(sound))

        except Exception as e:
            logging.warning(
                'Exception in processing sound "{title}": {exception}'.format(title=track.obj.get('title'),
                                                                              exception=e)
                )
    return sounds


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
    return render_template('index.html')


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
            'title': u'{location}, {upload_time:%b %d %Y, %H:%M}'.format(location=form.human_readable_location.data,
                                                                         upload_time=datetime.now()),
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


@app.route('/refresh')
def refresh_sounds():
    """
    Manually refresh sounds.
    """
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

