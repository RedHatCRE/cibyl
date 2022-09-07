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
from unittest.mock import Mock, patch

from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.environment import Environment
from cibyl.publisher import (JSONPublisher, PrintPublisher, PublisherFactory,
                             PublisherTarget)


class TestPrintPublisher(TestCase):
    """Testing print publisher component"""

    def setUp(self):
        self.env_name = "env1"
        self.environment = Environment(self.env_name)

    @patch('cibyl.outputs.cli.ci.env.factory.CIPrinterFactory.from_style')
    @patch('builtins.print')
    def test_publisher_publish(self, mock_print, mock_printer_factory):
        """Testing Publisher publish method"""

        text = 'output-text'

        printer = Mock()
        printer.print_environment = Mock()
        printer.print_environment.return_value = text

        mock_printer_factory.return_value = printer
        publisher = PrintPublisher()
        publisher.publish(environment=self.environment)

        printer.print_environment.assert_called_once_with(self.environment)

        mock_print.assert_called_once_with(text)


@patch('builtins.print')
class TestJSONPublisher(TestCase):
    """Testing json publisher component"""

    def setUp(self):
        self.text = '{"output": "output-text"}'
        self.publisher = JSONPublisher()
        self.env_name = "env1"
        self.printer = Mock()
        self.publisher.printer = self.printer
        self.publisher.printer.print_environment = Mock()
        self.publisher.printer.provider = Mock()
        self.publisher.printer.provider.indentation = 0
        self.publisher.printer.print_environment.return_value = self.text
        self.environment = Environment(self.env_name)

    def test_publisher_publish(self, mock_print):
        """Testing JSONPublisher publish method"""

        self.publisher.publish(environment=self.environment)

        self.printer.print_environment.assert_called_once()
        self.printer.print_environment.assert_called_with(self.environment)

        mock_print.assert_not_called()

    def test_publish_multiple_environments(self, mock_print):
        """Testing JSONPublisher publish method with multiple environments"""

        self.publisher.publish(environment=self.environment)
        self.publisher.publish(environment=self.environment)

        self.assertEqual(self.printer.print_environment.call_count, 2)
        mock_print.assert_not_called()

    def test_publish_multiple_environments_print(self, mock_print):
        """Testing JSONPublisher publish method with multiple environments and
        printing the output"""

        self.publisher.publish(environment=self.environment)
        self.publisher.publish(environment=self.environment)
        self.publisher.finish_publishing()

        self.assertEqual(self.printer.print_environment.call_count, 2)
        self.printer.print_environment.assert_called_with(self.environment)
        env = json.loads(self.text)
        expected = json.dumps({'environments': [env, env]}, indent=0)
        mock_print.assert_called_once_with(expected)


class TestPublisherFactory(TestCase):
    """Testing PublisherFactory component"""

    def test_json_style(self):
        """Test the creation of a Publisher for JSON output."""

        publisher = PublisherFactory.create_publisher(style=OutputStyle.JSON)
        self.assertIsInstance(publisher, JSONPublisher)
        self.assertEqual(publisher.style, OutputStyle.JSON)
        self.assertEqual(publisher.target, PublisherTarget.TERMINAL)
        self.assertEqual(publisher.query, QueryType.NONE)
        self.assertEqual(publisher.verbosity, 0)
        self.assertEqual(publisher.output, [])
        self.assertIsNone(publisher.output_file)

    def test_defaults(self):
        """Test the creation of a Publisher with default arguments."""

        publisher = PublisherFactory.create_publisher()
        self.assertIsInstance(publisher, PrintPublisher)
        self.assertEqual(publisher.style, OutputStyle.TEXT)
        self.assertEqual(publisher.target, PublisherTarget.TERMINAL)
        self.assertEqual(publisher.query, QueryType.NONE)
        self.assertEqual(publisher.verbosity, 0)
        self.assertIsNone(publisher.output_file)

    def test_colorized_style(self):
        """Test the creation of a Publisher with colorized style."""

        publisher = PublisherFactory.create_publisher(
                style=OutputStyle.COLORIZED)
        self.assertIsInstance(publisher, PrintPublisher)
        self.assertEqual(publisher.style, OutputStyle.COLORIZED)
        self.assertEqual(publisher.target, PublisherTarget.TERMINAL)
        self.assertEqual(publisher.query, QueryType.NONE)
        self.assertEqual(publisher.verbosity, 0)
        self.assertIsNone(publisher.output_file)
