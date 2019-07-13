from __future__ import absolute_import
from osscla.wsgi import app


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
