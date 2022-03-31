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

import cibyl.orchestrator
from cibyl.config import Config
from cibyl.exceptions.config import InvalidConfiguration
from cibyl.exceptions.source import NoValidSources
from cibyl.orchestrator import Orchestrator


class TestOrchestrator(TestCase):
    """Testing Orchestrator class"""

    def setUp(self):
        self.orchestrator = Orchestrator()

        self.invalid_config_data = {
            'environments': {
                'env1': {
                    'system1'}}}

        self.valid_single_env_config_data = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins'}}}}

        self.valid_multiple_envs_config_data = {
            'environments': {
                'env3': {
                    'system3': {
                        'system_type': 'jenkins'},
                    'system4': {
                        'system_type': 'zuul'}
                },
                'env4': {
                    'system1': {
                        'system_type': 'zuul'}
                }
            }
        }

        self.valid_env_sources = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins',
                        'sources': {
                            'jenkins': {
                                'driver': 'jenkins',
                                'url': ''
                                },
                            'jenkins2': {
                                'driver': 'jenkins',
                                'url': ''
                                }
                            }}}}}

    def test_orchestrator_config(self):
        """Testing Orchestrator config attribute and method"""
        self.assertTrue(hasattr(self.orchestrator, 'config'))

        path_to_config = 'some/path'

        factory_call = cibyl.orchestrator.ConfigFactory.from_path = Mock()
        factory_call.return_value = Mock()

        self.orchestrator.load_configuration(path_to_config)

        self.assertEqual(factory_call.return_value, self.orchestrator.config)

        factory_call.assert_called_once_with(path_to_config)

    def test_orchestrator_create_ci_environments(self):
        """Testing Orchestartor query method"""
        # No Environments
        self.assertEqual(self.orchestrator.create_ci_environments(), None)
        self.assertEqual(self.orchestrator.environments, [])

        # Invalid configuration
        self.orchestrator.config = Mock(Config())
        self.orchestrator.config.data = self.invalid_config_data
        with self.assertRaises(InvalidConfiguration):
            self.orchestrator.create_ci_environments()

        # Single environment configuration
        self.orchestrator.config.data = self.valid_single_env_config_data
        self.orchestrator.environments = []
        self.orchestrator.create_ci_environments()
        self.assertEqual(len(self.orchestrator.environments), 1)
        self.assertEqual(self.orchestrator.environments[0].name.value, 'env1')
        self.assertEqual(
            len(self.orchestrator.environments[0].systems.value), 1)
        self.assertEqual(
            self.orchestrator.environments[0].systems[0].name.value, 'system1')

        # Multiple environments configuration
        self.orchestrator.config.data = self.valid_multiple_envs_config_data
        self.orchestrator.environments = []
        self.orchestrator.create_ci_environments()
        self.assertEqual(len(self.orchestrator.environments), 2)
        self.assertEqual(self.orchestrator.environments[0].name.value, 'env3')
        self.assertEqual(self.orchestrator.environments[1].name.value, 'env4')
        self.assertEqual(
            len(self.orchestrator.environments[0].systems.value), 2)
        self.assertEqual(
            self.orchestrator.environments[0].systems[0].name.value, 'system3')
        self.assertEqual(
            self.orchestrator.environments[0].systems[1].name.value, 'system4')

    @patch("cibyl.orchestrator.get_source_method")
    def test_orchestrator_select_source(self, patched_method):
        """Testing Orchestartor select_source_method method"""
        self.orchestrator.config.data = self.valid_env_sources
        self.orchestrator.create_ci_environments()
        self.orchestrator.parser.ci_args["sources"] = Mock()
        self.orchestrator.parser.ci_args["sources"].value = ["jenkins"]
        system = Mock()
        system.name = Mock()
        system.name.value = "system"
        system.sources = Mock()
        source = Mock()
        source.name = "jenkins"
        system.sources = [source]
        argument = Mock()
        argument.func = None
        self.orchestrator.select_source_method(system, argument)
        patched_method.assert_called_with("system", [source], None)

    def test_orchestrator_select_source_invalid_source(self):
        """Testing Orchestrator select_source_method method with no valid
        source.
        """
        self.orchestrator.config.data = self.valid_env_sources
        self.orchestrator.create_ci_environments()
        self.orchestrator.parser.ci_args["sources"] = Mock()
        self.orchestrator.parser.ci_args["sources"].value = ["unknown"]
        system = Mock()
        system.name = Mock()
        system.name.value = "system"
        system.sources = Mock()
        source = Mock()
        source.name = "jenkins"
        system.sources = [source]
        argument = Mock()
        argument.func = None
        self.assertRaises(NoValidSources,
                          self.orchestrator.select_source_method,
                          system, argument)
