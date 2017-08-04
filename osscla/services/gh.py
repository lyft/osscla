import json

from pynamodb.exceptions import PutError
from github import Github

import osscla.services.sqs
from osscla import logger
from osscla.app import app
from osscla.models.signatures import Signature
from osscla.models.gh import PullRequest

HANDLED_PR_ACTIONS = ['opened', 'reopened', 'closed', 'synchronize']

GITHUB_CLIENT = None
ORG_MEMBERS = {}


def get_github_client():
    global GITHUB_CLIENT
    if GITHUB_CLIENT is None:
        GITHUB_CLIENT = Github(app.config['GITHUB_TOKEN'])
    return GITHUB_CLIENT


def update_org_membership():
    logger.info('Refreshing watched organization membership.')
    ghc = get_github_client()
    for org_name in app.config['WATCHED_ORGS']:
        org = ghc.get_organization(org_name)
        try:
            ORG_MEMBERS[org_name] = [m.login for m in org.get_members()]
        except Exception:
            logger.exception(
                'Failed to get org membership for {}'.format(org_name)
            )


def check_org_membership(user):
    for _, members in ORG_MEMBERS.iteritems():
        if user in members:
            return True
    return False


def queue_webhook(event_type, payload):
    if event_type == 'ping':
        # We want to return success on ping
        return
    elif event_type != 'pull_request':
        raise WebhookQueueError('Event type not supported')
    if 'repository' in payload:
        if payload['repository']['private']:
            logger.debug('Ignoring private repo...')
            # We only support public repos...
            return
    if payload['action'] not in HANDLED_PR_ACTIONS:
        # No need to raise an exception, just do nothing.
        return
    full_repo_name = payload['repository']['full_name']
    _queue_repo_action(
        payload['action'],
        full_repo_name,
        payload['number']
    )


def _queue_repo_action(action, full_repo_name, pr_number):
    sqs_client = osscla.services.sqs.get_client()
    q_url = osscla.services.sqs.get_queue_url()
    sqs_client.send_message(
        QueueUrl=q_url,
        MessageBody=json.dumps({
            'action': action,
            'full_repo_name': full_repo_name,
            'pr_number': pr_number
        }),
        MessageAttributes={
            'type': {
                'DataType': 'String',
                'StringValue': 'github_webhook'
            }
        }
    )


def update_pr_status(full_repo_name, pr_number):
    # We care about the author of all commits in the PR, so we'll find the
    # author of every commit, and ensure they have signatures.
    logger.debug(
        'Updating PR status for PR {}/{}'.format(full_repo_name, pr_number)
    )
    ghc = get_github_client()
    repo = ghc.get_repo(full_repo_name)
    pr = repo.get_pull(pr_number)
    commits = pr.get_commits()
    authors = []
    author_without_login = False
    for commit in commits:
        last_commit = commit
        try:
            authors.append(commit.author.login)
        except Exception:
            logger.exception('Failed to access the login name for a commit')
            author_without_login = True
    if author_without_login:
        last_commit.create_status(
            'failure',
            description=(
                'An author in one of the commits has no associated github name'
            ),
            target_url=app.config['SITE_URL'],
            context=app.config['GITHUB_STATUS_CONTEXT']
        )
    else:
        last_commit.create_status(
            'pending',
            context=app.config['GITHUB_STATUS_CONTEXT']
        )
    authors = list(set(authors))
    missing_authors = []
    # Check to see if the authors have signed the CLA
    for author in authors:
        if check_org_membership(author):
            # User is in a github org we have an org CLA with
            logger.debug('User {} has an org CLA'.format(author))
            continue
        try:
            Signature.get(author)
        except Signature.DoesNotExist:
            missing_authors.append(author)
    if missing_authors:
        for missing_author in missing_authors:
            # Save the PR info, so we can re-check the PR when signatures
            # occur.
            try:
                _pr = PullRequest(
                    username=missing_author,
                    pr='{0}:{1}'.format(repo.full_name, pr_number)
                )
                _pr.save(
                    pr__null=True
                )
                logger.debug(
                    'Saved PR for missing author {}'.format(missing_author)
                )
            except PutError:
                logger.debug('Skipping creation of existing PR in dynamo.')
        msg = ('The following authors related to commits in this PR have'
               ' not signed the CLA: {0}')
        msg = msg.format(', '.join(missing_authors))
        last_commit.create_status(
            'failure',
            description=msg,
            target_url=app.config['SITE_URL'],
            context=app.config['GITHUB_STATUS_CONTEXT']
        )
        logger.debug(
            'Submitted status for missing authors {0}.'.format(
                ','.join(missing_authors)
            )
        )
    else:
        last_commit.create_status(
            'success',
            description='All authors have signed the CLA.',
            target_url=app.config['SITE_URL'],
            context=app.config['GITHUB_STATUS_CONTEXT']
        )


def update_prs_for_username(username):
    logger.debug('Updating PRs for {}'.format(username))
    for pr in PullRequest.scan(username__eq=username):
        full_repo_name, pr_number = pr.pr.split(':')
        logger.debug(
            'Adding an SQS message for {}, {}'.format(full_repo_name, pr_number)
        )
        try:
            # Fake a synchronize repo action, to enqueue a PR check
            _queue_repo_action('synchronize', full_repo_name, int(pr_number))
        except Exception:
            logger.exception(
                'Failed to queue SQS message for {}/{}'.format(
                    full_repo_name,
                    pr_number
                )
            )
        try:
            # We know this user signed, so we can get rid of this PR in dynamo.
            pr.delete()
        except Exception:
            logger.exception(
                'Failed to delete PR {}/{}'.format(
                    full_repo_name,
                    pr_number
                )
            )


class WebhookQueueError(Exception):
    pass
