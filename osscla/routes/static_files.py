from __future__ import absolute_import
import os

from flask import send_from_directory, redirect, url_for

from osscla.app import app
from osscla import authnz
from osscla.cache_control import no_cache

ROUTE_PREFIX = app.config['ROUTE_PREFIX']


if ROUTE_PREFIX:
    @app.route('/')
    def index_no_prefix():
        return redirect(url_for('index'))


@app.route('{}/'.format(ROUTE_PREFIX))
@no_cache
@authnz.require_auth
def index():
    response = app.send_static_file('index.html')
    response.set_cookie(
        app.config['XSRF_COOKIE_NAME'],
        authnz.get_csrf_token()
    )
    return response


@app.route('/healthcheck')
def healthcheck():
    return '', 200


@app.route('{}/favicon.ico'.format(ROUTE_PREFIX))
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('{}/404.html'.format(ROUTE_PREFIX))
def not_found():
    return app.send_static_file('404.html')


@app.route('{}/robots.txt'.format(ROUTE_PREFIX))
def robots():
    return app.send_static_file('robots.txt')


@app.route('{}/clas/<path:path>'.format(ROUTE_PREFIX))
def clas(path):
    if not path.endswith('.html'):
        path = '{}.html'.format(path)
    if not app.config['CLA_DIRECTORY']:
        return '', 404
    return send_from_directory(app.config['CLA_DIRECTORY'], path)


@app.route('{}/bower_components/<path:path>'.format(ROUTE_PREFIX))
@no_cache
def components(path):
    return app.send_static_file(os.path.join('bower_components', path))


@app.route('{}/views/<path:path>'.format(ROUTE_PREFIX))
@no_cache
def views(path):
    return app.send_static_file(os.path.join('views', path))


@app.route('{}/images/<path:path>'.format(ROUTE_PREFIX))
@no_cache
def images(path):
    return app.send_static_file(os.path.join('images', path))


@app.route('{}/modules/<path:path>'.format(ROUTE_PREFIX))
@no_cache
def modules(path):
    return app.send_static_file(os.path.join('modules', path))


@app.route('{}/styles/<path:path>'.format(ROUTE_PREFIX))
@no_cache
def styles(path):
    return app.send_static_file(os.path.join('styles', path))
