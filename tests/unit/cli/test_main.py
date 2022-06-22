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

from cibyl.cli.main import OutputStyle, raw_parsing
from cibyl.exceptions.cli import InvalidArgument


class TestRawParsing(TestCase):
    """Tests for the -f CLI option.
    """

    def test_default_output(self):
        """Checks the default value for the option.
        """
        args = raw_parsing([])

        self.assertTrue(OutputStyle.COLORIZED, args['output_style'])

    @patch('cibyl.cli.main.OutputStyle.from_key')
    def test_f_arg(self, parse_call: Mock):
        """Checks that user's input is read.
        """
        style = 'raw'

        parse_call.return_value = OutputStyle.TEXT

        args = raw_parsing(['', '-f', style])

        self.assertTrue(OutputStyle.TEXT, args['output_style'])

        parse_call.assert_called_once_with(style)

    @patch('cibyl.cli.main.OutputStyle.from_key')
    def test_output_arg(self, parse_call: Mock):
        """Checks that --output-format also works.
        """
        output = 'raw'

        parse_call.return_value = OutputStyle.TEXT

        args = raw_parsing(['', '--output-format', output])

        self.assertTrue(OutputStyle.TEXT, args['output_style'])

        parse_call.assert_called_once_with(output)

    @patch('cibyl.cli.main.OutputStyle.from_key')
    def test_invalid_output_arg(self, parse_call: Mock):
        """Checks reaction to unknown style.
        """

        def raise_error(_):
            raise NotImplementedError

        output = 'invalid'

        parse_call.side_effect = raise_error

        with self.assertRaises(InvalidArgument):
            raw_parsing(['', '--output-format', output])

        parse_call.assert_called_once_with(output)
