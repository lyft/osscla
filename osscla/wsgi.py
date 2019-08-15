from __future__ import absolute_import
import guard

import osscla.authnz
from osscla.app import app
from osscla import routes  # noqa

CSP_POLICY = {
    'default-src': ["'self'"],
    'connect-src': [
        "'self'",
        "https://github.com"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'"  # for xeditable
    ]
}

app.wsgi_app = guard.ContentSecurityPolicy(app.wsgi_app, CSP_POLICY)

app.after_request(osscla.authnz.set_xfo_header)
