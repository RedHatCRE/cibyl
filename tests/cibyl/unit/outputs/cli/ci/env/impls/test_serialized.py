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
import json
from unittest import TestCase
from unittest.mock import Mock

from cibyl.outputs.cli.ci.env.impl.serialized import CIJSONPrinter


class TestCIJSONPrinter(TestCase):
    """Tests for :class:`CIJSONPrinter`.
    """

    def test_simple_environment(self):
        """Tests output of an environment without systems.
        """
        name = 'env'

        env = Mock()
        env.name.value = name
        env.systems = []

        printer = CIJSONPrinter()

        result = json.loads(printer.print_environment(env))

        self.assertEqual(
            {
                'name': name,
                'systems': {}
            },
            result
        )
