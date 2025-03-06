import os
import sys
from unittest import TestCase

from dirlay import Dir
from doctestcase import doctestcase


sys.path.insert(0, os.path.abspath('.'))

import tests.usage.multiple
import tests.usage.nested
import tests.usage.plain
import tests.usage.sugar


class SecretsManager:
    secrets_dir: Dir

    def setUp(self):
        self.secrets_dir.mktree(chdir=True)

    def tearDown(self):
        self.secrets_dir.rmtree()


@doctestcase(globals={'Settings': tests.usage.plain.Settings})
class UsagePlain(SecretsManager, TestCase):
    """
    Plain

    >>> Settings().model_dump()
    {'app_key': SecretStr('**********'), 'db': {'passwd': SecretStr('**********')}}
    """

    secrets_dir = Dir() | {
        'secrets': {
            'app_key': 'secret1',
            'db__passwd': 'secret2',
        },
    }


@doctestcase(globals={'Settings': tests.usage.nested.Settings})
class UsageNested(SecretsManager, TestCase):
    """
    Nested

    >>> Settings().model_dump()
    {'app_key': SecretStr('**********'), 'db': {'passwd': SecretStr('**********')}}
    """

    secrets_dir = Dir() | {
        'secrets': {
            'app_key': 'secret1',
            'db/passwd': 'secret2',
        },
    }


@doctestcase(globals={'Settings': tests.usage.multiple.Settings})
class UsageMultiple(SecretsManager, TestCase):
    """
    Multiple

    >>> Settings().model_dump()
    {'app_key': SecretStr('**********'), 'db': {'passwd': SecretStr('**********')}}
    """

    secrets_dir = Dir() | {
        'secrets': {
            'layer1/app_key': 'secret1',
            'layer2/db__passwd': 'secret2',
        },
    }


@doctestcase(globals={'Settings': tests.usage.sugar.Settings})
class UsageSugar(SecretsManager, TestCase):
    """
    Experimantal syntactic sugar

    >>> Settings().model_dump()
    {'app_key': SecretStr('**********'), 'db': {'passwd': SecretStr('**********')}}
    """

    secrets_dir = UsagePlain.secrets_dir
