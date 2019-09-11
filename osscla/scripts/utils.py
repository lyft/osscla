from __future__ import absolute_import
from __future__ import print_function
import json
import dateutil.parser
from flask_script import Command, Option

import osscla.services
from osscla.app import app
from osscla.models.signatures import Signature
import six


class CreateSQSQueue(Command):
    def run(self):
        sqs = osscla.services.get_boto_client(
            'sqs',
            endpoint_url=app.config['SQS_URL']
        )
        print(sqs.create_queue(
            QueueName=app.config['SQS_QUEUE_NAME']
        ))


class Import(Command):
    option_list = (
        Option('--input-file', dest='input_file'),
    )

    def run(self, input_file):
        with open(input_file, 'r') as f:
            signatures = json.load(f)
            signatures = signatures['signatures']
        for signature in signatures:
            Signature(
                username=signature['username'],
                emails=signature['emails'],
                name=signature['name'],
                ip_address=signature['ip_address'],
                cla_version=signature['cla_version'],
                modified_date=dateutil.parser.parse(signature['modified_date'])
            ).save()
            print('Signature saved for {}'.format(signature['username']))


class Export(Command):
    option_list = (
        Option('--output-file', dest='output_file'),
    )

    def run(self, output_file):
        export = []
        signatures = {}
        for signature in Signature.scan():
            if signature.username in signatures:
                signatures[signature.username]['emails'].append(signature.email)
                continue
            signatures[signature.username] = {
                'emails': [signature.email],
                'username': signature.username,
                'name': signature.name,
                'cla_version': signature.cla_version,
                'ip_address': signature.ip_address,
                'modified_date': signature.modified_date.isoformat()
            }
        for email, signature in six.iteritems(signatures):
            export.append(signature)

        out = json.dumps({'signatures': export})
        with open(output_file, 'w') as f:
            f.write(out)
        print('Exported')
