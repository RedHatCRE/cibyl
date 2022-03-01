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
import argparse
from unittest import TestCase

from cibyl.cli.argument import Argument
from cibyl.cli.parser import Parser


class TestParser(TestCase):
    """Testing CLI Parser"""

    def setUp(self):
        self.parser = Parser()
        self.default_debug = False
        self.test_argument = Argument('--test', arg_type=str,
                                      description='test')

    def test_parser_plugin_argument(self):
        """Testing parser plugin argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--plugin', 'openstack'])
        self.assertEqual(parsed_args.plugin, 'openstack')

    def test_parser_debug_argument(self):
        """Testing parser debug argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--debug'])
        self.assertTrue(parsed_args.debug)

    def test_parser_config_argument(self):
        """Testing parser config argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--config', '/some/path'])
        self.assertEqual(parsed_args.config_file_path, '/some/path')

    def test_parser_parse_args(self):
        """Testing parser extend method"""
        parsed_args_ns = self.parser.parse()
        self.assertEqual(vars(parsed_args_ns).get('debug'), self.default_debug)

    def test_parser_get_group(self):
        """Testing parser get_group method"""
        group = self.parser.get_group("test")
        self.assertIsNone(group)

        self.parser.extend([self.test_argument], 'test')
        group = self.parser.get_group("test")
        # pylint: disable=protected-access
        self.assertIsInstance(group, argparse._ArgumentGroup)
