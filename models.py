#!python
# -*- coding: utf-8 -*-
from collections import namedtuple
from wtforms import Form, DecimalField, StringField, FileField, validators


Sound = namedtuple('Sound', ['soundcloud_id',
                             'latitude',
                             'longitude',
                             'human_readable_location',
                             'description',
                             'datetime'])


class UploadSoundForm(Form):
    """
    Form to upload a Sound and associated information.
    """
    latitude = DecimalField(u'Latitude')
    longitude = DecimalField(u'Longitude')
    human_readable_location = StringField(u'Where did you record this sound?', validators=[validators.Length(max=140)])
    description = StringField(u'What is the sound? When did you record it?', validators=[validators.Length(max=140)])
    sound = FileField(u'Sound File')
