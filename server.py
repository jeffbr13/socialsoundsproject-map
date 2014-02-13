#!python
# -*- coding: utf-8 -*-
"""Back-end server for socialsoundsproject.com"""
import os

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from wtforms import Form, DecimalField, StringField, FileField, validators
import soundcloud

from data import sound_db


SERVER_URL = 'http://socialsoundsproject.herokuapp.com'
SOUNDCLOUD_CALLBACK_PATH = '/soundcloud/callback'

app = Flask(__name__)
soundcloud_client = soundcloud.Client(client_id=os.environ.get('SOUNDCLOUD_CLIENT_ID'),
                                      client_secret=os.environ.get('SOUNDCLOUD_CLIENT_SECRET'),
                                      redirect_uri=(SERVER_URL + SOUNDCLOUD_CALLBACK_PATH))


class UploadSoundForm(Form):
    """
    Form to upload a Sound and associated information.
    """
    latitude = DecimalField(u'Latitude')
    longitude = DecimalField(u'Longitude')
    human_readable_location = StringField(u'Location (human-readable)', validators=[validators.Length(max=140)])
    description = StringField(u'Description', validators=[validators.Length(max=140)])
    sound = FileField(u'Sound')


@app.route('/')
def index():
    """
    Serve the index page.
    """
    return render_template('index.html')


@app.route('/soundcloud/setup')
def setup():
    return redirect(soundcloud_client.authorize_url())


@app.route(SOUNDCLOUD_CALLBACK_PATH)
def soundcloud_callback():
    """
    Extract SoundCloud authorisation code.
    """
    code = request.args.get('code')
    access_token, expires, scope, refresh_token = soundcloud_client.exchange_token(code=request.args.get('code'))
    session = connection.SoundCloudSession()
    session['access_token'] = access_token
    session['expires'] = expires
    session['scope'] = scope
    session['refresh_token'] = refresh_token
    session.validate()
    session.save()
    return app.send_static_file('soundcloud-callback.html', user=soundcloud_client.get('/me'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_sound():
    """
    Serve or process the 'upload sound' form.
    """
    if request.method == 'POST':
        form = UploadSoundForm(request.form)
        if form.sound.data:
            track = soundcloud_client.post('/tracks', track={
                'title': form.human_readable_location,
                'description': form.description,
                'asset_data': form.sound.data
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
    sounds = [sound for sound in sound_db.sounds.find()]
    return jsonify(sounds=sounds)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

