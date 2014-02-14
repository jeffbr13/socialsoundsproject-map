#!python
# -*- coding: utf-8 -*-
"""Back-end server for socialsoundsproject.com"""
from os import environ

from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename
from wtforms import Form, DecimalField, StringField, FileField, validators
import soundcloud

from data import init_storage


SERVER_URL = 'http://socialsoundsproject.herokuapp.com'
SOUNDCLOUD_CALLBACK_PATH = '/soundcloud/callback'

app = Flask(__name__)
db = None
soundcloud_client = None


class UploadSoundForm(Form):
    """
    Form to upload a Sound and associated information.
    """
    latitude = DecimalField(u'Latitude')
    longitude = DecimalField(u'Longitude')
    human_readable_location = StringField(u'Location (human-readable)', validators=[validators.Length(max=140)])
    description = StringField(u'Description', validators=[validators.Length(max=140)])
    sound = FileField(u'Sound')


def init_soundcloud():
    """
    Returns SoundCloud client to use.
    """
    access_token = db.sessions.find_one()
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
    return redirect(soundcloud_client.authorize_url())


@app.route(SOUNDCLOUD_CALLBACK_PATH)
def soundcloud_callback():
    """
    Extract SoundCloud authorisation code.
    """
    #TODO: use Redis to stare these values
    db.session.drop()
    code = request.args.get('code')
    access_token = soundcloud_client.exchange_token(code=request.args.get('code')).access_token
    session = db.sessions.SoundCloudSession()
    session['access_token'] = access_token
    session.validate()
    session.save()
    return render_template('soundcloud-callback.html', user=soundcloud_client.get('/me'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_sound():
    """
    Serve or process the 'upload sound' form.
    """
    if request.method == 'POST':
        form = UploadSoundForm(request.form)

        if form.sound.data:
            sound = db.sounds.Sound()
            sound.location = (form.latitude, form.longitude)
            sound.human_readable_location = form.human_readable_location
            sound.description = form.description
            track = soundcloud_client.post('/tracks', track={
                'title': form.human_readable_location,
                'description': form.description,
                'asset_data': form.sound.data,
                'tag_list': 'geo:lat={lat} geo:lon={lon}'.format(lat=form.latitude, lon=form.longitude),
                'track_type': 'recording'
            })
            sound.soundcloud_id = track.id
            sound.validate()
            sound.save()
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
    #TODO: check for SoundCloud session in Redis at startup
    db = init_storage(environ.get('MONGOSOUP_URL'))
    soundcloud_client = init_soundcloud()
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

