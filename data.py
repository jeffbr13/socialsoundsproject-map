#!python
# -*- coding: utf-8 -*-
# from sqlalchemy import create_engine, Column, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, scoped_session


# Base = declarative_base()
# engine = create_engine('sqlite:///:memory:', echo=True)
# Session = sessionmaker(bind=engine)

# engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
# Base = declarative_base()
# Base.query = db_session.query_property()


# def init_db():
#     Base.metadata.create_all(bind=engine)


# class Sound(Base):
#     """
#     A sound ID with location information.

#     The audio data itself is hosted on SoundCloud.
#     """
#     __tablename__ = 'sounds'

#     id = Column(Integer, primary_key=True)
#     latitude = Column(Float)
#     longitude = Column(Float)
#     human_readable_location = Column(String(140))
#     description = Column(String(140))

#     def __repr__(self):
#         return u'<Sound: {lat}°N/{long}°E ({desc})>'.format(lat=self.latitude,
#                                                             long=self.longitude,
#                                                             desc=self.description)
from os import environ
from mongokit import Document, Connection



connection = Connection(host=environ.get('MONGODB_HOST'), port=int(environ.get('MONGODB_PORT')))


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate


@connection.register
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
        return u'<Sound: {lat}°N/{long}°E ({desc})>'.format(lat=self.location[0],
                                                            long=self.location[1],
                                                            desc=self.description)


@connection.register
class SoundCloudSession(Document):
    structure = {
        'access_token': basestring,
        'expires': None,
        'scope': None,
        'refresh_token': basestring
    }
