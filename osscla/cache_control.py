import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from functools import wraps
from flask import make_response

ONE_HOUR = 3600


def get_expires(max_age):
    """
    Get a timestamp suitable for an "Expires" header.

    Arguments:
        max_age: The max age before expiration, in seconds.

    Returns: A formated datetime string.
    """
    delta = datetime.timedelta(seconds=max_age)
    the_future = datetime.datetime.now() + delta
    time_stamp = mktime(the_future.timetuple())
    return format_date_time(time_stamp)


def cache_control(max_age):
    """A decorator to set the cache control and expires headers.

    This is designed to decorate a Flask view function.

    Arguments:
        max_age: The maximum age, in seconds, that the client should cache
            the response. If this is a negative number, it indicates that
            the client should never cache the response.

    Returns: The decorated view function.
    """
    def decorator(fcn):
        @wraps(fcn)
        def wrapper(*args, **kwargs):
            # Make sure this is a real response. If it already is,
            # `make_response` has no effect.
            resp = make_response(fcn(*args, **kwargs))
            # Set the Cache-Control header
            if max_age <= 0:
                resp.cache_control.public = False
                resp.cache_control.no_cache = True
                resp.cache_control.must_revalidate = True
                resp.cache_control.max_age = 0
            else:
                resp.cache_control.public = True
                resp.cache_control.max_age = max_age
            # Set the Expires header
            resp.headers['Expires'] = get_expires(max_age)
            return resp
        return wrapper
    return decorator


def no_cache(fcn):
    """
    Route decorator for content that must never be cached.

    This should be used for dynamic content (like checking login status).
    """
    return cache_control(-ONE_HOUR)(fcn)
