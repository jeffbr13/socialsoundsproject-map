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
cache = None
soundcloud_client = None


def init_cache(redis_url):
    logging.debug('Connecting to Redis cache...')
    url = urlparse(redis_url)
    return redis.Redis(host=url.hostname, port=url.port, password=url.password)


def init_soundcloud(token_cache):
    """
    Returns SoundCloud client to use.
    """
    logging.debug('Initialising SoundCloud client...')
    access_token = token_cache.get('soundcloud:access_token')
    if access_token:
        return soundcloud.Client(client_id=environ.get('SOUNDCLOUD_CLIENT_ID'),
                                 client_secret=environ.get('SOUNDCLOUD_CLIENT_SECRET'),
                                 redirect_uri=(SERVER_URL + SOUNDCLOUD_CALLBACK_PATH),
                                 access_token=access_token)
    else:
        return soundcloud.Client(client_id=environ.get('SOUNDCLOUD_CLIENT_ID'),
                                 client_secret=environ.get('SOUNDCLOUD_CLIENT_SECRET'),
                                 redirect_uri=(SERVER_URL + SOUNDCLOUD_CALLBACK_PATH))


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
    cache.delete('soundcloud:access_token')
    cache.delete('soundcloud:scope')
    soundcloud_client = init_soundcloud()
    return redirect(soundcloud_client.authorize_url())


@app.route(SOUNDCLOUD_CALLBACK_PATH)
def soundcloud_callback():
    """
    Extract SoundCloud authorisation code.
    """
    code = request.args.get('code')
    access_token = soundcloud_client.exchange_token(code=request.args.get('code'))
    cache.set('soundcloud:access_token', access_token.access_token)
    cache.set('soundcloud:scope', access_token.scope)
    return render_template('soundcloud-callback.html', user=soundcloud_client.get('/me'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_sound():
    """
    Serve or process the 'upload sound' form.
    """
    if request.method == 'POST':
        form = UploadSoundForm(request.form)
        if form.sound.data:
            track = soundcloud_client.post('/tracks', track={
                'title': '{location}, {upload_time:%b %d %Y, %H:%M}'.format(location=form.human_readable_location,
                                                                            upload_time=datetime.now()),
                'description': form.description,
                'asset_data': form.sound.data,
                'tag_list': 'geo:lat={lat} geo:lon={lon}'.format(lat=form.latitude, lon=form.longitude),
                'track_type': 'recording',
                'license': 'cc-by-sa',
                'downloadable': True,
            })
            return redirect(track.permalink_url)

    else:
        form = UploadSoundForm()

    return render_template('upload-sound.html', form=form)


@app.route('/sounds.json')
def all_sounds():
    """
    Return JSON for all sounds.
    """
    #TODO: retrieve data from SoundCloud sounds instead of storing separately (upload_sound() shows fields used).
    sounds = [sound for sound in db.sounds.find()]
    return jsonify(sounds=sounds)


if __name__ == '__main__':
    logging.info('Starting server...')
    cache = init_cache(environ.get('REDISCLOUD_URL'))
    soundcloud_client = init_soundcloud(cache)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5000))
    logging.debug('Launching Flask app...')
    app.run(host='0.0.0.0', port=port, debug=True)

