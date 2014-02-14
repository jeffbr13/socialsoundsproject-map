#!python
# -*- coding: utf-8 -*-
from mongokit import Document, Connection



def init_storage(*args, **kwargs):
    """
    Returns MongoDB database to use.
    """
    connection = Connection(*args, **kwargs)
    connection.register([Sound, SoundCloudSession])
    return connection.get_default_database()


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate


class Sound(Document):
    structure = {
        'soundcloud_id': int,
        'location': (float,float),
        'human_readable_location': unicode,
        'description': unicode
    }

    required = ['soundcloud_id', 'location']
    validators = {
        'human_readable_location': max_length(140),
        'description': max_length(140)
    }

    use_dot_notation = True

    def __repr__(self):
        return u'<Sound: {lat}°N/{long}°E ({loc} - {desc})>'.format(lat=self.location[0],
                                                                    loc=self.human_readable_location,
                                                                    long=self.location[1],
                                                                    desc=self.description)


class SoundCloudSession(Document):
    structure = {
        'access_token': basestring,
        'expires': None,
        'scope': None,
        'refresh_token': basestring
    }

    use_dot_notation = True
    required = ['access_token']
