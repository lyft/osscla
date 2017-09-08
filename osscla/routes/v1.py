import hmac
import hashlib
try:
    from hmac import compare_digest
    has_compare_digest = True
except ImportError:
    has_compare_digest = False

import flask
from flask import request
from flask import abort
from flask import jsonify
from flask import redirect

import osscla.services
from osscla import authnz
from osscla import logger
from osscla.app import app
from osscla.models.signatures import Signature
from osscla.services.gh import WebhookQueueError

ROUTE_PREFIX = app.config['ROUTE_PREFIX']


@app.route('{0}/v1/adminlogin'.format(ROUTE_PREFIX), methods=['GET'])
@authnz.require_auth
def admin_login():
    redirect(flask.url_for('index'))


@app.route('{0}/v1/user/info'.format(ROUTE_PREFIX), methods=['GET'])
@authnz.require_auth
def get_user_info():
    """Get the email address of the currently logged-in user."""
    return jsonify({
        'username': authnz.get_logged_in_username(),
        'admin': authnz.user_in_role('admin'),
        'xsrf_cookie_name': app.config['XSRF_COOKIE_NAME']
    })


@app.route('{0}/v1/current_cla'.format(ROUTE_PREFIX), methods=['GET'])
def get_current_cla():
    """Get the current CLA version."""
    return jsonify({'cla_version': app.config['CURRENT_CLA_VERSION']})


def _get_addr():
    if app.config['IP_HEADER']:
        addr = request.headers[app.config['IP_HEADER']]
        logger.debug(
            'Using {}, got {}'.format(app.config['IP_HEADER'], addr)
        )
    elif app.config['USE_XFF']:
        addr = request.access_route[-1]
        logger.debug('Using XFF, got {}'.format(addr))
    else:
        if request.remote_addr is None or request.remote_addr == '':
            addr = 'n/a'
        else:
            addr = request.remote_addr
        logger.debug('Using remote_addr, got {}'.format(addr))
    return addr


@app.route('{0}/v1/signature/<username>'.format(ROUTE_PREFIX), methods=['PUT'])
@authnz.require_auth
@authnz.require_csrf_token
def put_signature(username):
    data = request.get_json()
    if authnz.user_in_role('admin'):
        admin_update = data.get('admin_update', False)
    else:
        if username != authnz.get_logged_in_username():
            abort(403)
        admin_update = False

    try:
        signature = Signature.get(username)
    except Signature.DoesNotExist:
        signature = None

    orgs = []
    if admin_update:
        if signature is not None:
            # TODO: Make it possible for admins to edit existing signatures.
            # For now we're not allowing the modification of signatures to make
            # life easier for ourselves.
            return jsonify(
                {'error': 'Signature for this user already exists.'},
            ), 400
        # admin adding a signature
        if 'emails' not in data:
            return jsonify(
                {'error': 'No emails provided.'}
            ), 400
        if 'orgs' not in data:
            return jsonify(
                {'error': 'No orgs provided.'}
            ), 400
        emails = data['emails']
        orgs = data['orgs']
        if not orgs:
            return jsonify(
                {'error': 'orgs must not be an empty list.'}
            ), 400
        if signature is None:
            addr = 'n/a'
        else:
            addr = signature.addr
    else:
        # self-adding a signature
        if 'orgs' in data:
            # We only allow modification of orgs for admin updates
            return jsonify(
                {'error': 'Not allowed to modify orgs.'}
            ), 403
        if signature is not None:
            orgs = signature.orgs
        emails = []
        _emails = authnz.get_logged_in_user_email()
        for email in _emails:
            if not email.get('verified'):
                continue
            emails.append(email['email'])
        if not emails:
            return jsonify(
                {'error': 'No verified emails found for your github account'}
            ), 400
        addr = _get_addr()
    if not isinstance(emails, list):
        return jsonify(
            {'error': 'emails must be a list.'}
        ), 400
    if not isinstance(orgs, list):
        return jsonify(
            {'error': 'orgs must be a list.'}
        ), 400
    if not emails:
        return jsonify(
            {'error': 'emails must not be an empty list'}
        ), 400
    # Store signature
    signature = Signature(
        username=username,
        emails=emails,
        name=authnz.get_logged_in_name(),
        orgs=orgs,
        ip_address=addr
    )
    signature.save()

    return jsonify({
        'signature': {
            'username': signature.username,
            'emails': list(signature.emails),
            'name': signature.name,
            'cla_version': signature.cla_version,
            'modified_date': signature.modified_date,
            'orgs': list(signature.orgs)
        }
    })


@app.route('{0}/v1/signature/<username>'.format(ROUTE_PREFIX), methods=['GET'])
@authnz.require_auth
def get_signature(username):
    if not authnz.user_in_role('admin'):
        if username != authnz.get_logged_in_username():
            abort(403)
    try:
        signature = Signature.get(username)
        if signature.emails is None:
            signature.emails = []
        if signature.orgs is None:
            signature.orgs = []
        return jsonify({
            'signature': {
                'username': signature.username,
                'emails': list(signature.emails),
                'name': signature.name,
                'cla_version': signature.cla_version,
                'modified_date': signature.modified_date,
                'orgs': list(signature.orgs)
            }
        })
    except Signature.DoesNotExist:
        return jsonify({'signature': {}})


@app.route('{0}/v1/signatures'.format(ROUTE_PREFIX), methods=['GET'])
@authnz.require_auth
def get_signatures():
    signatures = []
    for signature in Signature.scan():
        if signature.emails is None:
            signature.emails = []
        if signature.orgs is None:
            signature.orgs = []
        signatures.append({
            'username': signature.username,
            'emails': list(signature.emails),
            'name': signature.name,
            'cla_version': signature.cla_version,
            'ip_address': signature.ip_address,
            'modified_date': signature.modified_date,
            'orgs': list(signature.orgs)
        })
    return jsonify({'signatures': signatures})


@app.route('{0}/v1/organizations'.format(ROUTE_PREFIX), methods=['GET'])
@authnz.require_auth
def get_organizations():
    return jsonify({'orgs': app.config['CCLA_ORGS']})


def _compare_digest(x, y):
    """Implementation of hmac.compare_digest from Python 3
    This reduces the vulnerability to a timing attack.
    """
    if has_compare_digest:
        return compare_digest(x, y)

    if not (isinstance(x, bytes) and isinstance(y, bytes)):
        raise TypeError('both inputs should be instances of bytes')

    result = len(x) == len(y)
    for i in range(len(x)):
        try:
            result &= x[i] == y[i]
        except IndexError:
            result = False
    return result


@app.route('{0}/v1/github/notification'.format(ROUTE_PREFIX), methods=['POST'])
def receive_ghwebhook():
    # Before we do anything, make sure this actually came from a webhook we've
    # setup.
    if app.config['GITHUB_WEBHOOK_SECRET']:
        mac = hmac.new(
            app.config['GITHUB_WEBHOOK_SECRET'],
            msg=request.data,
            digestmod=hashlib.sha1
        )
        version, signature = request.headers.get('X-Hub-Signature').split('=')
        if version != 'sha1':
            abort(403)
        if not _compare_digest(
                mac.hexdigest().encode('utf-8'),
                signature.encode('utf-8')):
            abort(403)

    # Now queue the message to be handled async.
    try:
        osscla.services.gh.queue_webhook(
            request.headers["X-GitHub-Event"],
            request.json
        )
    except WebhookQueueError as e:
        return jsonify({'status': 'failure', 'error': str(e)}), 500

    return jsonify({'status': 'success'}), 200
