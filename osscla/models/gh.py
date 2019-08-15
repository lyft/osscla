from __future__ import absolute_import
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

from osscla.app import app


class PullRequest(Model):
    class Meta:
        table_name = app.config.get('DYNAMODB_TABLE_PR')
        if app.config.get('DYNAMODB_URL'):
            host = app.config.get('DYNAMODB_URL')
        region = app.config.get('AWS_DEFAULT_REGION')

    username = UnicodeAttribute(hash_key=True)
    pr = UnicodeAttribute(range_key=True)
