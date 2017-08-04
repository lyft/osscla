import osscla.services
from osscla.app import app

QUEUE_URL = None


def get_client():
    if app.config['SQS_URL']:
        return osscla.services.get_boto_client(
            'sqs',
            endpoint_url=app.config['SQS_URL']
        )
    else:
        return osscla.services.get_boto_client('sqs')


def get_queue_url():
    global QUEUE_URL

    if QUEUE_URL is None:
        client = get_client()
        QUEUE_URL = client.get_queue_url(
            QueueName=app.config['SQS_QUEUE_NAME']
        )['QueueUrl']

    return QUEUE_URL
