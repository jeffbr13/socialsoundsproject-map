socialsoundsproject-map
=======================

The [Social Sounds Project map][] shows sounds uploaded to Social Sounds Projects across the UK,
and allows anyone to upload a sound and mark it on the map.


The Social Sounds Project webapp is currently served by a single [Heroku](http://heroku.com) dyno,
and uses a [Redis Cloud](http://redislabs.com/redis-cloud) addon to store authentication credentials
across sessions.

Sound data and metadata is stored on
the [Social Sounds Project SoundCloud page](https://soundcloud.com/socialsoundsproject/).




## Usage

### Requirements

- `python`
- `pip`
- [`git`](http://www.git-scm.com/)
- [`virtualenvwrapper`](http://virtualenvwrapper.readthedocs.org/en/latest/)

### Environment Variables

The following environment variables need to be set for the server to run correctly:

```sh
export SOUNDCLOUD_CLIENT_SECRET='...'
export SOUNDCLOUD_CLIENT_ID='...'
export REDISCLOUD_URL='redis://...'
```

If developing locally, it's recommended that you put these variables into a `.env` file and
use [`autoenv`](https://github.com/kennethreitz/autoenv) to load them upon entering the project directory.


### Setup

```sh
git clone https://github.com/jeffbr13/socialsoundsproject-map
cd socialsoundsproject-map
mkvirtualenv -a . -r requirements.txt socialsoundsproject-map
```

### Run the server

```sh
python server.py
```



[Social Sounds Project map]: http://socialsoundsproject.com
