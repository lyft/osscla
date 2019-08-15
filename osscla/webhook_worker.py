from __future__ import absolute_import
import gevent
import gevent.monkey
gevent.monkey.patch_all(thread=False)
import gevent.pool
import json
import signal

from osscla import logger
from osscla.app import app
from osscla.services import stats
from osscla.services import sqs
from osscla.services import gh

STATE = {
    'shutdown': False
}


def bootstrap():
    global SHUTDOWN

    watch_orgs()

    def finalizer(signal, frame):
        logger.info("SIGTERM caught, shutting down")
        STATE['shutdown'] = True
    signal.signal(signal.SIGTERM, finalizer)


def wait_available(pool, pool_name):
    statsd = stats.get_statsd_client()
    if pool.full():
        statsd.incr('%s.pool.full' % pool_name)
        pool.wait_available()
    return not STATE['shutdown']


def watch_orgs():
    try:
        gh.update_org_membership()
    except Exception:
        logger.exception('Failed to update org membership.')

    return gevent.spawn_later(
        app.config['WATCHED_ORGS_RELOAD_INTERVAL'],
        watch_orgs
    )


def handle_signature(message):
    data = json.loads(message['Body'])
    gh.update_prs_for_username(data['username'])


def handle_webhook(message):
    data = json.loads(message['Body'])
    if data['action'] not in gh.HANDLED_PR_ACTIONS:
        logger.debug('Skipping unhandled action {}'.format(data['action']))
        return
    if data['action'] == 'closed':
        logger.debug('Skipping closed action')
        return
    gh.update_pr_status(data['full_repo_name'], data['pr_number'])


def handle_message(client, queue_url):
    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['SentTimestamp'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=60,
            WaitTimeSeconds=10
        )
        if 'Messages' in response:
            messages = response['Messages']
            message = messages[0]
            if 'type' not in message['MessageAttributes']:
                logger.error('SQS message does not have a type attribute.')
                return
            m_type = message['MessageAttributes']['type']['StringValue']
            logger.debug('Received SQS message of type {}'.format(m_type))
            if m_type == 'github_webhook':
                try:
                    handle_webhook(message)
                except Exception:
                    logger.exception(
                        'Failed to handle webhook SQS message'
                    )
                    return
            elif m_type == 'signature':
                try:
                    handle_signature(message)
                except Exception:
                    logger.exception(
                        'Failed to handle signature SQS message'
                    )
                    return
            else:
                logger.error(
                    '{0} is an unsupported message type.'.format(m_type)
                )
            client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
        else:
            logger.debug('No messages, continuing')
            return
    except Exception:
        logger.exception('General error')


def main():
    bootstrap()
    client = sqs.get_client()
    queue_url = sqs.get_queue_url()
    queue_pool = gevent.pool.Pool(app.config['WEBHOOK_WORKER_CONCURRENCY'])
    while wait_available(queue_pool, 'webhookpool'):
        queue_pool.spawn(handle_message, client, queue_url)


if __name__ == "__main__":
    main()
