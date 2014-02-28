#!python
# -*- coding: utf-8 -*-
from collections import namedtuple
from wtforms import Form, DecimalField, StringField, FileField, validators


LOCATIONS = [
    {
        "name": "edinburgh",
        "human_readable_name": "Edinburgh",
        "centre": [55.947, -3.2],
        "scale": 11
    },
    {
        "name": "glasgow",
        "human_readable_name": "Glasgow",
        "centre": [55.859, -4.285],
        "scale": 11
    },
    {
        "name": "peak_district",
        "human_readable_name": "Peak District",
        "centre": [53.283, -1.761],
        "scale": 11
    },
    {
        "name": "west_coast",
        "human_readable_name": "Off The Grid",
        "centre": [56.547, -5.690],
        "scale": 11
    },
]


Sound = namedtuple('Sound', ['soundcloud_id',
                             'latitude',
                             'longitude',
                             'human_readable_location',
                             'description'])


class UploadSoundForm(Form):
    """
    Form to upload a Sound and associated information.
    """
    latitude = DecimalField(u'Latitude')
    longitude = DecimalField(u'Longitude')
    human_readable_location = StringField(u'Where did you record this sound?', validators=[validators.Length(max=140)])
    description = StringField(u'What is the sound? When did you record it?', validators=[validators.Length(max=140)])
    sound = FileField(u'Sound File')
