#!python
# -*- coding: utf-8 -*-
from wtforms import Form, DecimalField, StringField, FileField, validators


class Sound():
    # structure = {
    #     'soundcloud_id': int,
    #     'location': (float,float),
    #     'human_readable_location': unicode,
    #     'description': unicode
    # }

    def __repr__(self):
        return u'<Sound: {lat}°N/{long}°E ({loc} - {desc})>'.format(lat=self.location[0],
                                                                    loc=self.human_readable_location,
                                                                    long=self.location[1],
                                                                    desc=self.description)


class UploadSoundForm(Form):
    """
    Form to upload a Sound and associated information.
    """
    latitude = DecimalField(u'Latitude')
    longitude = DecimalField(u'Longitude')
    human_readable_location = StringField(u'Location (human-readable)', validators=[validators.Length(max=140)])
    description = StringField(u'Description', validators=[validators.Length(max=140)])
    sound = FileField(u'Sound')
