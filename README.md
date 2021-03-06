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
export SECRET_KEY='…'                     # random secret string - feel free to mash the keyboard for this
export SOUNDCLOUD_AUTH_PATH='…'           # secret address on server to authenticate your SoundCloud account
export SOUNDCLOUD_CLIENT_SECRET='…'       # SoundCloud API Secret
export SOUNDCLOUD_CLIENT_ID='…'           # SoundCloud API ID
export REDISCLOUD_URL='redis://…'         # Redis Cloud server address

export ADMIN_EMAIL='incase@thingsbreak.net'

# SMTP variables in order to email notification of breakages to $ADMIN_EMAIL
export SMTP_HOST='…'
export SMTP_PORT='25'
export SMTP_USERNAME='…'
export SMTP_PASSWORD='…'
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

To authenticate your server with your SoundCloud account, visit `http://{server-address}/{SOUNDCLOUD_AUTH_PATH}`,
with `SOUNDCLOUD_AUTH_PATH` being a string stored in an [environment variable](#environment-variables).



## [License](https://www.mozilla.org/MPL/2.0/)

Source code in this repository is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at <http://mozilla.org/MPL/2.0/>.



[Social Sounds Project map]: http://socialsoundsproject.com
