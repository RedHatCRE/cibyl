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

from cibyl.cli.validator import Validator
from cibyl.config import AppConfig
from cibyl.exceptions.model import (InvalidEnvironment, InvalidSystem,
                                    NoEnabledSystem, NoValidSystem)
from cibyl.exceptions.source import NoValidSources
from cibyl.orchestrator import Orchestrator


def get_all_systems(envs):
    """Extract all systems from environments to a flat list."""
    systems = []
    for env in envs:
        systems.extend(env.systems)
    return systems


class TestValidator(TestCase):
    """Testing Validator class"""

    def setUp(self):

        self.orchestrator = Orchestrator()
        self.ci_args = {}

        self.config = {
            'environments': {
                'env': {
                    'system3': {
                        'system_type': 'jenkins',
                        'sources': {}},
                    'system4': {
                        'system_type': 'zuul',
                        'sources': {}}
                },
                'env1': {
                    'system1': {
                        'system_type': 'zuul',
                        'sources': {
                            'zuul': {
                                'driver': 'zuul',
                                'url': ''
                                },
                            'zuul2': {
                                'driver': 'zuul',
                                'url': ''
                                }
                            }}
                }
            }
        }
        self.config_enable = {
            'environments': {
                'env': {
                    'system3': {
                        'system_type': 'jenkins',
                        'sources': {},
                        'enabled': False},
                    'system4': {
                        'system_type': 'zuul',
                        'sources': {},
                        'enabled': False}
                },
                'env1': {
                    'system1': {
                        'system_type': 'zuul',
                        'enabled': False,
                        'sources': {
                            'zuul': {
                                'driver': 'zuul',
                                'url': ''
                                }
                            }}
                }
            }
        }

    def tests_validator_validate_environments(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["env"]
        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs = validator.validate_environments(original_envs)
        systems = get_all_systems(envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(2, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)
        self.assertEqual("system4", systems[1].name.value)
        self.assertEqual("zuul", systems[1].system_type.value)

    def tests_validator_validate_environments_systems(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["env"]
        self.ci_args["systems"] = Mock()
        self.ci_args["systems"].value = ["system3"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs = validator.validate_environments(original_envs)
        systems = get_all_systems(envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)

    def tests_validator_validate_environments_system_type(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["env"]
        self.ci_args["system_type"] = Mock()
        self.ci_args["system_type"].value = ["jenkins"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs = validator.validate_environments(original_envs)
        systems = get_all_systems(envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)

    def tests_validator_validate_environments_system_type_no_systems(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["env"]
        self.ci_args["system_type"] = Mock()
        self.ci_args["system_type"].value = ["unk"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        self.assertRaises(NoValidSystem,
                          validator.validate_environments,
                          original_envs)

    def tests_validator_validate_environments_no_envs(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["unknown"]
        self.ci_args["system_type"] = Mock()
        self.ci_args["system_type"].value = ["jenkins"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        self.assertRaises(InvalidEnvironment,
                          validator.validate_environments,
                          original_envs)

    def tests_validator_validate_environments_no_systems(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["systems"] = Mock()
        self.ci_args["systems"].value = ["unknown"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        self.assertRaises(InvalidSystem,
                          validator.validate_environments,
                          original_envs)

    def test_validator_validate_sources(self):
        """Test Validator validate_environments with sources."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["sources"] = Mock()
        self.ci_args["sources"].value = ["zuul"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments
        envs = validator.validate_environments(original_envs)
        systems = get_all_systems(envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system1", systems[0].name.value)
        self.assertEqual("zuul", systems[0].system_type.value)
        self.assertEqual("env1", envs[0].name.value)
        system = systems[0]
        self.assertEqual(2, len(system.sources.value))
        # test that only the selected source is enabled
        self.assertTrue(system.sources[0].enabled)
        self.assertFalse(system.sources[1].enabled)

    def test_validator_validate_no_sources(self):
        """Test Validator validate_environments with no sources."""
        self.orchestrator.config = AppConfig(data=self.config)
        self.orchestrator.create_ci_environments()
        self.ci_args["envs"] = Mock()
        self.ci_args["envs"].value = ["env"]
        self.ci_args["sources"] = Mock()
        self.ci_args["sources"].value = ["zuul"]

        original_envs = self.orchestrator.environments
        validator = Validator(self.ci_args)
        self.assertRaises(NoValidSources,
                          validator.validate_environments,
                          original_envs)

    def test_validator_validate_no_enabled_system(self):
        """Test Validator validate_environments with no enabled systems."""
        self.orchestrator.config = AppConfig(data=self.config_enable)
        self.orchestrator.create_ci_environments()

        original_envs = self.orchestrator.environments
        validator = Validator(self.ci_args)
        self.assertRaises(NoEnabledSystem,
                          validator.validate_environments,
                          original_envs)

    def test_validator_validate_override_no_enabled_system(self):
        """Test Validator validate_environments overriding disabled systems."""
        self.orchestrator.config = AppConfig(data=self.config_enable)
        self.orchestrator.create_ci_environments()
        self.ci_args["systems"] = Mock()
        self.ci_args["systems"].value = ["system3", "system4"]

        original_envs = self.orchestrator.environments
        validator = Validator(self.ci_args)
        envs = validator.validate_environments(original_envs)
        systems = get_all_systems(envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(2, len(systems))
        self.assertEqual("env", envs[0].name.value)
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("system4", systems[1].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)
        self.assertEqual("zuul", systems[1].system_type.value)
