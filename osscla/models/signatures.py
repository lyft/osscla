import json
from datetime import datetime

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from pynamodb.attributes import UnicodeSetAttribute
from pynamodb.attributes import UTCDateTimeAttribute

import osscla.services.sqs
from osscla import logger
from osscla.app import app


class Signature(Model):
    class Meta:
        table_name = app.config.get('DYNAMODB_TABLE')
        if app.config.get('DYNAMODB_URL'):
            host = app.config.get('DYNAMODB_URL')
        region = app.config.get('AWS_DEFAULT_REGION')

    username = UnicodeAttribute(hash_key=True)
    emails = UnicodeSetAttribute()
    name = UnicodeAttribute()
    orgs = UnicodeSetAttribute(null=True, default=[])
    ip_address = UnicodeAttribute()
    cla_version = UnicodeAttribute(default=app.config['CURRENT_CLA_VERSION'])
    modified_date = UTCDateTimeAttribute(default=datetime.now)

    def save(self, *args, **kwargs):
        # First, actually save the signature in dynamo
        super(Signature, self).save(*args, **kwargs)
        # Next, enqueue a message for async actions based on this signature
        try:
            sqs_client = osscla.services.sqs.get_client()
            q_url = osscla.services.sqs.get_queue_url()
            sqs_client.send_message(
                QueueUrl=q_url,
                MessageBody=json.dumps({
                    'username': self.username
                }),
                MessageAttributes={
                    'type': {
                        'DataType': 'String',
                        'StringValue': 'signature'
                    }
                }
            )
        except Exception:
            logger.exception(
                'Failed to queue signature message for {}'.format(self.username)
            )
