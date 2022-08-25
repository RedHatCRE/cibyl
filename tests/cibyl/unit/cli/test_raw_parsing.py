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
import logging
from unittest import TestCase

from cibyl.cli.main import raw_parsing
from cibyl.cli.output import OutputStyle


class TestRawParsing(TestCase):
    """Test raw_parsing from main."""

    def test_parser_plugin_argument(self):
        """Tests parser plugin argument."""
        parse_args = ['cibyl', '--plugin', 'openstack', 'unknown']
        args = raw_parsing(parse_args)
        self.assertEqual(args['plugins'], ['openstack', 'unknown'])

    def test_parser_debug_argument(self):
        """Tests parser debug argument."""
        parse_args = ['cibyl', '--debug']
        args = raw_parsing(parse_args)
        self.assertTrue(args['debug'])
        self.assertEqual(args['logging'], logging.DEBUG)

    def test_parser_config_argument(self):
        """Tests parser config argument."""
        parse_args = ['cibyl', '--config', '/some/path']
        args = raw_parsing(parse_args)
        self.assertEqual(args['config_file_path'], '/some/path')

    def test_parser_help_argument(self):
        """Tests parser help argument."""
        parse_args = ['cibyl', '--help']
        args = raw_parsing(parse_args)
        self.assertTrue(args['help'])

    def test_parser_log_file_argument(self):
        """Tests parser log_file argument."""
        parse_args = ['cibyl', '--log-file', '/some/path']
        args = raw_parsing(parse_args)
        self.assertEqual(args['log_file'], '/some/path')

    def test_parser_log_mode_argument(self):
        """Tests parser log_mode argument."""
        parse_args = ['cibyl', '--log-mode', 'terminal']
        args = raw_parsing(parse_args)
        self.assertEqual(args['log_mode'], 'terminal')

    def test_parser_output_format_argument(self):
        """Tests parser output format argument."""
        parse_args = ['cibyl', '--output-format', 'text']
        args = raw_parsing(parse_args)
        self.assertEqual(args['output_style'], OutputStyle.from_key('text'))

    def test_parser_all_arguments(self):
        """Tests that all arguments are parsed."""
        parse_args = ['cibyl', '-c', 'path', '-h', '--log-file', 'log',
                      '--log-mode', 'terminal', '-d', '-p', 'plugin1',
                      'plugin2', '-f', 'text']
        args = raw_parsing(parse_args)
        self.assertEqual(args['config_file_path'], 'path')
        self.assertTrue(args['help'])
        self.assertEqual(args['log_file'], 'log')
        self.assertEqual(args['log_mode'], 'terminal')
        self.assertTrue(args['debug'])
        self.assertEqual(args['logging'], logging.DEBUG)
        self.assertEqual(args['plugins'], ['plugin1', 'plugin2'])
        self.assertEqual(args['output_style'], OutputStyle.from_key('text'))

    def test_parser_plugin_argument_with_query(self):
        """Tests parser plugin argument with subcommands."""
        parse_args = ['cibyl', '--plugin', 'openstack', 'unknown', 'query',
                      '--jobs']
        args = raw_parsing(parse_args)
        self.assertEqual(args['plugins'], ['openstack', 'unknown'])

    def test_parser_plugin_argument_with_features(self):
        """Tests parser plugin argument with subcommands."""
        parse_args = ['cibyl', '--plugin', 'openstack', 'unknown', 'features']

        args = raw_parsing(parse_args)
        self.assertEqual(args['plugins'], ['openstack', 'unknown'])

    def test_parser_plugin_argument_with_spec(self):
        """Tests parser plugin argument with subcommands."""
        parse_args = ['cibyl', '--plugin', 'openstack', 'unknown', 'spec']

        args = raw_parsing(parse_args)
        self.assertEqual(args['plugins'], ['openstack', 'unknown'])
