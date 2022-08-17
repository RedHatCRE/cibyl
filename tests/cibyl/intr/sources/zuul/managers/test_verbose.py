"""
#    Copyright 2022 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
from unittest import TestCase
from unittest.mock import Mock

from cibyl.sources.zuul.managers.verbose import VerboseManager
from cibyl.sources.zuul.source import Zuul


class TestVerboseManager(TestCase):
    """Tests for :class:`VerboseManager`.
    """

    def test_tenants_query(self):
        """Checks that tenants are retrieved from the host when the argument
        is found.
        """
        kwargs = {}

        api = Mock()

        manager = VerboseManager(api)

        source = Zuul(
            name='test-source',
            driver='zuul',
            url=Mock(),
            manager=manager
        )

        result = source.get_tenants(**kwargs)
        models = result.value
