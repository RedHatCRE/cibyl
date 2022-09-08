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
from cibyl.cli.output import OutputArrangement
from cibyl.exceptions.cli import InvalidArgument


class TestOutputStyle(TestCase):
    """Tests for the '-f' CLI option.
    """

    def test_default_output(self):
        """Checks the default value for the option.
        """
        args = raw_parsing([])

        self.assertEqual(OutputStyle.COLORIZED, args['output_style'])

    @patch('cibyl.cli.main.OutputStyle.from_key')
    def test_f_arg(self, parse_call: Mock):
        """Checks that user's input is read.
        """
        style = 'raw'

        parse_call.return_value = OutputStyle.TEXT

        args = raw_parsing(['', '-f', style])

        self.assertEqual(OutputStyle.TEXT, args['output_style'])

        parse_call.assert_called_once_with(style)

    @patch('cibyl.cli.main.OutputStyle.from_key')
    def test_output_arg(self, parse_call: Mock):
        """Checks that --output-format also works.
        """
        output = 'raw'

        parse_call.return_value = OutputStyle.TEXT

        args = raw_parsing(['', '--output-format', output])

        self.assertEqual(OutputStyle.TEXT, args['output_style'])

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


class TestOutputArrangement(TestCase):
    """Tests for the '-a' option of the CLI.
    """

    def test_default_output(self):
        """Checks the value that is picked if the option is not defined.
        """
        args = raw_parsing([])

        self.assertEqual(
            OutputArrangement.HIERARCHY,
            args['output_arrangement']
        )

    @patch('cibyl.cli.main.OutputArrangement.from_key')
    def test_a_arg(self, parse_call: Mock):
        """Checks that the arrangement can be defined through the '-a'
        argument.
        """
        arrangement = 'hierarchy'

        parse_call.return_value = OutputArrangement.HIERARCHY

        args = raw_parsing(['', '-a', arrangement])

        self.assertEqual(
            OutputArrangement.HIERARCHY,
            args['output_arrangement']
        )

        parse_call.assert_called_once_with(arrangement)

    @patch('cibyl.cli.main.OutputArrangement.from_key')
    def test_output_arg(self, parse_call: Mock):
        """Checks that the arrangement can be defined through the
        '--output-arrangement' argument.
        '"""
        arrangement = 'hierarchy'

        parse_call.return_value = OutputArrangement.HIERARCHY

        args = raw_parsing(['', '--output-arrangement', arrangement])

        self.assertEqual(
            OutputArrangement.HIERARCHY,
            args['output_arrangement']
        )

        parse_call.assert_called_once_with(arrangement)

    @patch('cibyl.cli.main.OutputArrangement.from_key')
    def test_invalid_output_arg(self, parse_call: Mock):
        """Checks reaction to invalid option.
        '"""

        def raise_error(_):
            raise NotImplementedError

        arrangement = 'hierarchy'

        parse_call.side_effect = raise_error

        with self.assertRaises(InvalidArgument):
            raw_parsing(['', '--output-arrangement', arrangement])

        parse_call.assert_called_once_with(arrangement)
