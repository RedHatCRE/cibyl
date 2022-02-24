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

from cibyl.config import Config
from cibyl.exceptions.config import InvalidConfiguration
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

    def test_orchestrator_config(self):
        """Testing Orchestrator config attribute and method"""
        self.assertTrue(hasattr(self.orchestrator, 'config'))

        self.orchestrator.config = Mock()
        self.orchestrator.load_configuration()

        self.orchestrator.config.load.assert_called()

    def test_orchestrator_query(self):
        """Testing Orchestrator query method"""
        self.assertEqual(self.orchestrator.run_query(), None)

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
