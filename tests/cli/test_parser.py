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
from cibyl.models.ci.environment import Environment


class TestParser(TestCase):
    """Testing CLI Parser"""

    def setUp(self):
        self.parser = Parser()
        self.default_debug = False
        self.test_argument = Argument('--test', arg_type=str,
                                      description='test')
        self.environment = Environment(name='test-env')
        self.environment.arguments = self.environment.API.get(
            'name').get('arguments')

    def test_parser_plugin_argument(self):
        """Tests parser plugin argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--plugin', 'openstack'])
        self.assertEqual(parsed_args.plugin, 'openstack')

    def test_parser_debug_argument(self):
        """Tests parser debug argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--debug'])
        self.assertTrue(parsed_args.debug)

    def test_parser_config_argument(self):
        """Tests parser config argument"""
        parsed_args = self.parser.argument_parser.parse_args(
            ['--config', '/some/path'])
        self.assertEqual(parsed_args.config_file_path, '/some/path')

    def test_parser_extend(self):
        """Tests parser extend method"""
        self.parser.extend(self.environment.arguments, 'Environment')
        # Extend again and see if a message is logged about it
        with self.assertLogs('cibyl.cli.parser', level='DEBUG'):
            self.parser.extend(self.environment.arguments, 'Environment')

    def test_parser_parse_args(self):
        """Testing parser extend method"""
        self.parser.parse()
        self.assertEqual(self.parser.app_args, {'plugin': 'openstack'})
        self.assertEqual(self.parser.ci_args, {})

        self.parser.extend(self.environment.arguments, 'Environment')
        self.parser.parse(['--env-name', 'env1', '--plugin', 'openshift'])
        self.assertEqual(self.parser.app_args, {'plugin': 'openshift'})
        self.assertEqual(self.parser.ci_args,
                         {'env_name': Argument(
                             name='env_name', arg_type=str,
                             description='Name of the environment', nargs=1,
                             func=None, populated=False, level=0,
                             value=['env1'])})

    def test_parser_get_group(self):
        """Tests parser get_group method"""
        group = self.parser.get_group("test")
        self.assertIsNone(group)

        self.parser.extend([self.test_argument], 'test')
        group = self.parser.get_group("test")
        # pylint: disable=protected-access
        self.assertIsInstance(group, argparse._ArgumentGroup)
