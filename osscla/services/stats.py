from __future__ import absolute_import
import statsd

from osscla.app import app

STATS_CLIENT = None


def get_statsd_client():
    global STATS_CLIENT
    if STATS_CLIENT is None:
        STATS_CLIENT = statsd.StatsClient(
            app.config['STATSD_HOST'],
            app.config['STATSD_PORT'],
            prefix=['STATSD_PREFIX']
        )
    return STATS_CLIENT
