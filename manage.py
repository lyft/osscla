#!/usr/bin/env python

from __future__ import absolute_import
from flask.ext.script import Manager

from osscla.app import app
from osscla.scripts.utils import Import
from osscla.scripts.utils import Export
from osscla.scripts.utils import CreateSQSQueue

manager = Manager(app)

manager.add_command("import", Import)
manager.add_command("export", Export)
manager.add_command("create-queue", CreateSQSQueue)

if __name__ == "__main__":
    manager.run()
