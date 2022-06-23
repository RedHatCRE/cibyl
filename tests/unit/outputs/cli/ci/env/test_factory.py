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

from cibyl.cli.output import OutputStyle
from cibyl.outputs.cli.ci.env.factory import CIPrinterFactory
from cibyl.utils.colors import ClearText, DefaultPalette


class TestCIPrinterFactory(TestCase):
    def test_unknown_style(self):
        query = Mock()
        verbosity = Mock()

        factory = CIPrinterFactory()

        with self.assertRaises(NotImplementedError):
            factory.from_style(-1, query, verbosity)

    def test_returns_clear_text_printer(self):
        query = Mock()
        verbosity = Mock()

        factory = CIPrinterFactory()

        result = factory.from_style(OutputStyle.TEXT, query, verbosity)

        self.assertEqual(query, result.query)
        self.assertEqual(verbosity, result.verbosity)

        self.assertIsInstance(result.palette, ClearText)

    def test_returns_colored_text_printer(self):
        query = Mock()
        verbosity = Mock()

        factory = CIPrinterFactory()

        result = factory.from_style(OutputStyle.COLORIZED, query, verbosity)

        self.assertEqual(query, result.query)
        self.assertEqual(verbosity, result.verbosity)

        self.assertIsInstance(result.palette, DefaultPalette)
