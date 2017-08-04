# osscla

AngularJS and Flask service for a click-through CLA, with github auth.

## Installation

### Docker installation

It's necessary to export your configuration variables before running osscla.
You can either specify them as multiple -e options, or you can put them into an
an environment file and use --env-file.

```bash
docker pull lyft/osscla
docker run --env-file my_config -t lyft/osscla
```

### Manual installation

Assumptions:

1. Using Ubuntu or Debian (please help with non-Ubuntu/Debian install
   instructions!)
1. Using gunicorn as the wsgi server
1. Installation location: /srv/osscla/venv
1. venv location: /srv/osscla/venv
1. node\_modules location: /srv/osscla/node\_modules

Make a virtualenv and install pip requirements:

```bash
cd /srv
git clone https://github.com/lyft/osscla
cd osscla
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Build the frontend

```bash
cd /srv/osscla
sudo apt-get install -y ruby-full npm nodejs nodejs-legacy git git-core
gem install compass
npm install grunt-cli
npm install
node_modules/grunt-cli/bin/grunt build
```

## Configuration

See [the settings file](https://github.com/lyft/osscla/blob/master/osscla/settings.py)
for specific configuration options.

Excluding the CLA HTML and admin list, all configuration options are passed in through the
environment.

### Docker vs bash

Note that below the format of the configuration is given in bash format for
defining and exporting environment variables. Docker environment files have a
slightly different format than bash. Here's an example of the difference:

In bash format:

```bash
export MY_VARIABLE='MY_VALUE'
```

In docker env file format, you don't export the variable, and the value
shouldn't be quoted, since everything after the equal sign is considered part
of the value. So, in a docker environment file, you'd define the same variable
and value like this:

In docker format:

```
MY_VARIABLE=MY_VALUE
```

### Github auth setup

You'll need to create a github applicaton through your settings, then you'll
need to set the client id, consumer secret and user agent in osscla:

```bash
export CREDENTIALS_GITHUB_OAUTH_CLIENT_ID='...'
export CREDENTIALS_GITHUB_OAUTH_CONSUMER_SECRET='...'
export GITHUB_OAUTH_USER_AGENT='My unique user agent (this really should be specific to your app)'
export AUTHOMATIC_SALT='some_long_random_string_that_is_used_to_salt_the_oauth_flow'
```

### CSRF protection

You'll need to set a random string that can be used as a secret for CSRF token
generation:

```bash
export CREDENTIALS_SESSION_SECRET='some_long_random_string_that_is_used_to_generate_csrf_tokens'
```

### DynamoDB setup

osscla uses DynamoDB. You'll need to update your service's IAM role to allow
osscla to use (and optionally create) its DynamoDB table. You'll need to pass
in configuration telling osscla its table name, its region, and whether or not
to create its table.

```bash
export DYNAMODB_TABLE=osscla-production-useast1
export DYNAMODB_CREATE_TABLE=true
export AWS_DEFAULT_REGION=us-east-1
```

### Admin access

osscla can allow a list of admins to view a list of CLAs that have been signed.
Provide osscla with a list of admins (as github usernames) in a YAML file.

```bash
export ADMINS_FILE='/etc/osscla/admins.yaml'
```

### CLA settings

osscla lets you set a current CLA version, and to provide a location with CLAs,
in html form (as version.html i.e.: 1.0.html, 1.1.html, etc.). When an end-user
visits osscla, it'll tell them if their CLA is out of date. It'll display the
current version of the CLA in the form.

```bash
export CURRENT_CLA_VERSION='1.0'
export CLA_DIRECTORY=/mnt/osscla/clas'
```

## Run osscla

In the following we assume _my\_config_ is a bash file with exports for all of
the necessary settings discussed in the configuration section.

```bash
source my_config
cd /srv/osscla
source venv/bin/activate
gunicorn wsgi:app --workers=2 -k gevent
```
