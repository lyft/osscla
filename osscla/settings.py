from os import getenv

def bool_env(var_name, default=False):
    """
    Get an environment variable coerced to a boolean value.
    Example:
        Bash:
            $ export SOME_VAL=True
        settings.py:
            SOME_VAL = bool_env('SOME_VAL', False)
    Arguments:
        var_name: The name of the environment variable.
        default: The default to use if `var_name` is not specified in the
                 environment.
    Returns: `var_name` or `default` coerced to a boolean using the following
        rules:
            "False", "false" or "" => False
            Any other non-empty string => True
    """
    test_val = getenv(var_name, default)
    # Explicitly check for 'False', 'false', and '0' since all non-empty
    # string are normally coerced to True.
    if test_val in ('False', 'false', '0'):
        return False
    return bool(test_val)


def float_env(var_name, default=0.0):
    """
    Get an environment variable coerced to a float value.
    This has the same arguments as bool_env. If a value cannot be coerced to a
    float, a ValueError will be raised.
    """
    return float(getenv(var_name, default))


def int_env(var_name, default=0):
    """
    Get an environment variable coerced to an integer value.
    This has the same arguments as bool_env. If a value cannot be coerced to an
    integer, a ValueError will be raised.
    """
    return int(getenv(var_name, default))


def str_env(var_name, default=''):
    """
    Get an environment variable as a string.
    This has the same arguments as bool_env.
    """
    return getenv(var_name, default)

DEBUG = bool_env('DEBUG', False)
if DEBUG:
    _DEFAULT_LOG_LEVEL = 'DEBUG'
else:
    _DEFAULT_LOG_LEVEL = 'INFO'
LOG_LEVEL = str_env('LOG_LEVEL', _DEFAULT_LOG_LEVEL)
PORT = int_env('PORT', 80)
STATIC_FOLDER = str_env('STATIC_FOLDER', 'public')

# Statsd metrics

# A statsd host
STATSD_HOST = str_env('STATSD_HOST', 'localhost')
# A statsd port
STATSD_PORT = int_env('STATSD_PORT', 8125)
# A statsd prefix for metrics
STATSD_PREFIX = str_env('STATSD_PREFIX', 'osscla')

# Github authentication

# The client ID and secret provided by github's developer settings console.
GITHUB_OAUTH_CLIENT_ID = str_env('CREDENTIALS_GITHUB_OAUTH_CLIENT_ID')
GITHUB_OAUTH_CONSUMER_SECRET = str_env(
    'CREDENTIALS_GITHUB_OAUTH_CONSUMER_SECRET'
)
# A user agent to identify your application to github.
GITHUB_OAUTH_USER_AGENT = str_env('GITHUB_OAUTH_USER_AGENT')
# A randomly generated string that can be used as a salt for the OAuth2 flow.
AUTHOMATIC_SALT = str_env('CREDENTIALS_AUTHOMATIC_SALT')

# The login name of an organization whose members will be treated as admins.
# admins are allowed to see all CLA signatures.
ORGANIZATION = str_env('ORGANIZATION')

# SSL redirection and HSTS
SSLIFY = bool_env('SSLIFY', True)

# CSRF protection
SESSION_SECRET = str_env('CREDENTIALS_SESSION_SECRET')

# Dynamo storage

# The DynamoDB URL
# Example: http://localhost:8000
DYNAMODB_URL = str_env('DYNAMODB_URL')
# The DynamoDB table to use for CLA signatures.
# Example: mydynamodbtable
DYNAMODB_TABLE = str_env('DYNAMODB_TABLE')
# Whether or not to allow osscla to generate its own DynamoDB table via
# PynamoDB.
DYNAMODB_CREATE_TABLE = bool_env('DYNAMODB_CREATE_TABLE', False)
# Must be set to the region the server is running.
AWS_DEFAULT_REGION = str_env('AWS_DEFAULT_REGION', 'us-east-1')

# CLA settings

# The current version of the CLA
CURRENT_CLA_VERSION = str_env('CURRENT_CLA_VERSION')
# The directory that contains all of the CLAs, in html format.
CLA_DIRECTORY = str_env('CLA_DIRECTORY')

# Route prefix
ROUTE_PREFIX = str_env('ROUTE_PREFIX', '')

# IP address collection settings.

# If X-Forwarded-For header is set, use the header, rather than remote_addr
USE_XFF = bool_env('USE_XFF', True)
# Custom request header that contains the real IP address of the client
IP_HEADER = str_env('IP_HEADER', '')

# Github webhook and API support for CLA checks against PRs.

# Token for talking to github API
GITHUB_TOKEN = str_env('CREDENTIALS_GITHUB_TOKEN')
# Secret for verifying github webhooks
GITHUB_WEBHOOK_SECRET = str_env('CREDENTIALS_GITHUB_WEBHOOK_SECRET')
# Context for github status checks
GITHUB_STATUS_CONTEXT = str_env('GITHUB_STATUS_CONTEXT', 'CLA check')
# URL for linking CLA check details to
SITE_URL = str_env('SITE_URL')

# The SQS URL
# Example: http://localhost
SQS_URL = str_env('SQS_URL')
# SQS queue name for enqueuing webhooks
SQS_QUEUE_NAME = str_env('SQS_QUEUE_NAME')
# gevent pool concurrency for handling enqueued webhooks
WEBHOOK_WORKER_CONCURRENCY = int_env('WEBHOOK_WORKER_CONCURRENCY', 1)

# A comma separated list of github orgs to fetch membership of, for whitelisted
# CLA checking.
WATCHED_ORGS = str_env('WATCHED_ORGS', '').split(',')
# Frequency for reloading watched organization membership
WATCHED_ORGS_RELOAD_INTERVAL = int_env('WATCHED_ORGS_RELOAD_INTERVAL', 1860)
# ORGS that have a Corporate CLA signed
CCLA_ORGS = str_env('CCLA_ORGS', '').split(',')

# The DynamoDB table to use for storing PR references for CLA checks.
# Example: mydynamodbtable-pr
DYNAMODB_TABLE_PR = str_env('DYNAMODB_TABLE_PR')


def get(name, default=None):
    "Get the value of a variable in the settings module scope."
    return globals().get(name, default)
