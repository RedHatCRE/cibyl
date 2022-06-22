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
from unittest.mock import Mock, patch

from cibyl.cli.output import OutputStyle
from cibyl.models.ci.base.environment import Environment
from cibyl.publisher import Publisher


class TestOrchestrator(TestCase):
    """Testing publisher component"""

    def setUp(self):
        self.publisher = Publisher()
        self.env_name = "env1"
        self.environment = Environment(self.env_name)

    @patch('cibyl.outputs.cli.ci.factory.CIPrinterFactory.from_style')
    @patch('builtins.print')
    def test_publisher_publish(self, mock_print, mock_printer_factory):
        """Testing Publisher publish method"""
        style = OutputStyle.TEXT
        text = 'output-text'

        printer = Mock()
        printer.print_environment = Mock()
        printer.print_environment.return_value = text

        mock_printer_factory.return_value = printer

        self.publisher.publish(
            environment=self.environment,
            target="terminal",
            style=style
        )

        printer.print_environment.assert_called_once_with(self.environment)

        mock_print.assert_called_once_with(text)
