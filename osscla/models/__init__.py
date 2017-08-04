import time

from pynamodb.exceptions import TableError

from osscla.app import app
from osscla.models.signatures import Signature
from osscla.models.gh import PullRequest


def _create_table(model):
    i = 0
    # This loop is absurd, but there's race conditions with dynamodb local
    while i < 5:
        try:
            if not model.exists():
                model.create_table(
                    read_capacity_units=10,
                    write_capacity_units=10,
                    wait=True
                )
            return
        except TableError:
            i = i + 1
            time.sleep(2)


# Only used when using dynamodb local
if app.config.get('DYNAMODB_CREATE_TABLE'):
    for model in [Signature, PullRequest]:
        _create_table(model)
