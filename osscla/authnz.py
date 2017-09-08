import fnmatch
import random
import copy

from authomatic import Authomatic
from authomatic.providers import oauth2
from authomatic.adapters import WerkzeugAdapter
from flask import g, abort, session, request, make_response, redirect, url_for
from werkzeug.security import safe_str_cmp
from functools import wraps

from osscla import logger
from osscla.app import app

authomatic_config = {
    'github': {
        'class_': oauth2.GitHub,
        'consumer_key': app.config['GITHUB_OAUTH_CLIENT_ID'],
        'consumer_secret': app.config['GITHUB_OAUTH_CONSUMER_SECRET'],
        'access_headers': {
            'User-Agent': app.config['GITHUB_OAUTH_USER_AGENT']
        },
        'scope': [
            'user:email'
        ]
    }
}
authomatic_config_admin = copy.deepcopy(authomatic_config)
authomatic_config_admin['github']['scope'].append('read:org')

_authomatic = Authomatic(
    authomatic_config,
    app.config['AUTHOMATIC_SALT']
)
_authomatic_admin = Authomatic(
    authomatic_config_admin,
    app.config['AUTHOMATIC_SALT']
)

PRIVILEGES = {
    'user': [
        'index',
        'get_user_info',
        'put_signature',
        'get_signature'
    ],
    'admin': ['*']
}


def get_logged_in_user_email():
    '''
    Retrieve logged-in user's email that is stored in session
    '''
    if session.get('github_oauth2') and session['github_oauth2'].get('email'):
        return session['github_oauth2']['email']
    else:
        raise UserEmailNotFound()


class UserEmailNotFound(Exception):
    pass


class AdminAccessNeeded(Exception):
    pass


def get_logged_in_user_orgs():
    '''
    Retrieve logged-in user's github organizations stored in session
    '''
    if session.get('github_oauth2') and session['github_oauth2'].get('orgs'):
        return session['github_oauth2']['orgs']
    else:
        raise OrgsNotFound()


class OrgsNotFound(Exception):
    pass


def get_logged_in_username():
    '''
    Retrieve logged-in user's username that is stored in session
    '''
    return session['github_oauth2']['username']


def get_logged_in_name():
    '''
    Retrieve logged-in user's full name that is stored in session
    '''
    return session['github_oauth2']['name']


def user_in_role(role):
    if role == g.auth_role:
        return True
    return False


def role_has_privilege(role, privilege):
    for _privilege in PRIVILEGES[role]:
        if fnmatch.fnmatch(privilege, _privilege):
            return True
    return False


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            email = get_logged_in_user_email()
            is_admin = False
            try:
                orgs = get_logged_in_user_orgs()
                for org in orgs:
                    if org.get('login') == app.config['ORGANIZATION']:
                        is_admin = True
            except OrgsNotFound:
                if not role_has_privilege('user', f.func_name):
                    raise AdminAccessNeeded()
                else:
                    pass
            if is_admin:
                role = 'admin'
            else:
                role = 'user'
            g.auth_role = role
        except (UserEmailNotFound, AdminAccessNeeded):
            logger.info('Attempting to log in a user using Github auth')
            response = make_response()
            if request.is_secure:
                secure_cookie = True
            else:
                secure_cookie = False
            if role_has_privilege('user', f.func_name):
                result = _authomatic.login(
                    WerkzeugAdapter(request, response),
                    'github',
                    session=session,
                    session_saver=lambda: app.save_session(session, response),
                    secure_cookie=secure_cookie
                )
                fetch_orgs = False
            else:
                # This function requires admin, we need to fetch the orgs,
                # which requires different scopes, use the admin login.
                result = _authomatic_admin.login(
                    WerkzeugAdapter(request, response),
                    'github',
                    session=session,
                    session_saver=lambda: app.save_session(session, response),
                    secure_cookie=secure_cookie
                )
                fetch_orgs = True
            if result:
                if result.error:
                    msg = 'Github auth failed with error: {0}'
                    logger.error(msg.format(result.error.message))
                    return abort(403)
                if result.user:
                    result.user.update()
                    user = result.user
                    session['github_oauth2'] = {}
                    session['github_oauth2']['name'] = user.name
                    session['github_oauth2']['username'] = user.username
                    g.auth_type = 'oauth'
                    email_addresses = _authomatic.access(
                        credentials=user.credentials,
                        url='https://api.github.com/user/emails'
                    ).data
                    session['github_oauth2']['email'] = email_addresses
                    if fetch_orgs:
                        organizations = _authomatic.access(
                            credentials=user.credentials,
                            url='https://api.github.com/user/orgs'
                        ).data
                        session['github_oauth2']['orgs'] = organizations
                    # TODO: find a way to save the angular args
                    # authomatic adds url params google auth has stripped the
                    # angular args anyway, so let's just redirect back to the
                    # index.
                    return redirect(url_for('index'))
            return response
        if role_has_privilege(role, f.func_name):
            return f(*args, **kwargs)
        else:
            msg = ('User with email {0}, role {1}, attempted to access'
                   ' function {2} without correct privileges')
            logger.warning(msg.format(email, role, f.func_name))
            return abort(403)
    return decorated


def get_csrf_token():
    cookie_name = app.config['XSRF_COOKIE_NAME']
    if cookie_name not in session:
        set_csrf_token()
    return session.get(app.config['XSRF_COOKIE_NAME'])


def set_csrf_token():
    session[app.config['XSRF_COOKIE_NAME']] = '{0:x}'.format(
        random.SystemRandom().getrandbits(160)
    )


def check_csrf_token():
    token = request.headers.get('X-XSRF-TOKEN')
    if not token:
        return False
    return safe_str_cmp(token, get_csrf_token())


def require_csrf_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_csrf_token():
            return f(*args, **kwargs)
        return abort(401)
    return decorated
