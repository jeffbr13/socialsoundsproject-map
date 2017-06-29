#!python
# -*- coding: utf-8 -*-
"""Back-end server for socialsoundsproject.com"""
import logging
from os import environ as env

import soundcloud
from flask import Flask, render_template, request, jsonify, redirect, flash
from flask_redis import FlaskRedis

from models import LOCATIONS, Sound, UploadSoundForm


SERVER_URL = env['SERVER_URL']
REDIS_URL = env['REDISCLOUD_URL']
SOUNDCLOUD_CLIENT = None
SOUNDCLOUD_SOUNDS = None

logging.basicConfig(level=logging.DEBUG if env.get('DEBUG') else logging.INFO)

app = Flask(__name__)
app.secret_key = env['SECRET_KEY']
REDIS_CACHE = FlaskRedis(app)


def init_soundcloud(token_store):
    """
    Returns SoundCloud client to use.
    """
    logging.debug('Initialising SoundCloud client...')
    return soundcloud.Client(client_id=env['SOUNDCLOUD_CLIENT_ID'],
                             client_secret=env['SOUNDCLOUD_CLIENT_SECRET'],
                             username=env['SOUNDCLOUD_ACCOUNT_USERNAME'],
                             password=env['SOUNDCLOUD_ACCOUNT_PASSWORD'])


def get_sounds(soundcloud_client):
    """
    Get all geolocated Sounds in the authenticated user's stream.
    """
    logging.info('Fetching sound data from authenticated user\'s SoundCloud stream.')
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
    if not SOUNDCLOUD_SOUNDS:
        flash(
            'No sounds found. Try authenticating to SoundCloud at secret URL http://{server-address}/${SOUNDCLOUD_AUTH_PATH}.',
            'danger')

    return render_template('index.html', locations=LOCATIONS)


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
    SOUNDCLOUD_CLIENT = init_soundcloud(REDIS_CACHE)
    SOUNDCLOUD_SOUNDS = get_sounds(SOUNDCLOUD_CLIENT)
    return redirect('/')


if __name__ == '__main__':
    logging.info('Starting server...')
    SOUNDCLOUD_CLIENT = init_soundcloud(REDIS_CACHE)
    try:
        SOUNDCLOUD_SOUNDS = get_sounds(SOUNDCLOUD_CLIENT)
    except Exception as e:
        logging.exception('Error getting Soundcloud sounds:')
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(env.get('PORT', 5000))
    logging.debug('Launching Flask app...')
    app.run(host='0.0.0.0', port=port, debug=bool(env.get('DEBUG', False)))
