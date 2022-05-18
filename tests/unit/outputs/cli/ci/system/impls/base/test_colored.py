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

from cibyl.outputs.cli.ci.system.impls.base.colored import \
    ColoredBaseSystemPrinter


class TestColoredBaseSystemPrinter(TestCase):
    """Tests for :class:`ColoredBaseSystemPrinter`.
    """

    def test_system_verbosity_0(self):
        """Checks output for a system with verbosity level set to 0.
        """
        system = Mock()
        system.name.value = 'TEST'

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = lambda text: text

        printer = ColoredBaseSystemPrinter(verbosity=0, palette=palette)

        self.assertEqual(
            'System: TEST',
            printer.print_system(system)
        )

        palette.blue.assert_called_once_with('System: ')

    def test_system_verbosity_1(self):
        """Checks output for a system with verbosity level set to 1.
        """
        system = Mock()
        system.name.value = 'TEST'
        system.system_type.value = 'TYPE'

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = lambda text: text

        printer = ColoredBaseSystemPrinter(verbosity=1, palette=palette)

        self.assertEqual(
            'System: TEST (type: TYPE)',
            printer.print_system(system)
        )

        palette.blue.assert_called_once_with('System: ')
