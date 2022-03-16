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
from cibyl.exceptions.model import NoValidEnvironment, NoValidSystem
from cibyl.orchestrator import Orchestrator


class TestValidator(TestCase):
    """Testing Validator class"""

    def setUp(self):

        self.orchestrator = Orchestrator()
        self.ci_args = {}

        self.config = {
            'environments': {
                'env': {
                    'system3': {
                        'system_type': 'jenkins'},
                    'system4': {
                        'system_type': 'zuul'}
                },
                'env1': {
                    'system1': {
                        'system_type': 'zuul'}
                }
            }
        }

    def tests_validator_validate_environments(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["env_name"] = Mock()
        self.ci_args["env_name"].value = ["env"]
        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs, systems = validator.validate_environments(original_envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(2, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)
        self.assertEqual("system4", systems[1].name.value)
        self.assertEqual("zuul", systems[1].system_type.value)

    def tests_validator_validate_environments_systems(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["env_name"] = Mock()
        self.ci_args["env_name"].value = ["env"]
        self.ci_args["systems"] = Mock()
        self.ci_args["systems"].value = ["system3"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs, systems = validator.validate_environments(original_envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)

    def tests_validator_validate_environments_system_name(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["env_name"] = Mock()
        self.ci_args["env_name"].value = ["env"]
        self.ci_args["system_name"] = Mock()
        self.ci_args["system_name"].value = ["system3"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs, systems = validator.validate_environments(original_envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)

    def tests_validator_validate_environments_system_type(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["env_name"] = Mock()
        self.ci_args["env_name"].value = ["env"]
        self.ci_args["system_type"] = Mock()
        self.ci_args["system_type"].value = ["jenkins"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        envs, systems = validator.validate_environments(original_envs)
        self.assertEqual(1, len(envs))
        self.assertEqual(1, len(systems))
        self.assertEqual("system3", systems[0].name.value)
        self.assertEqual("jenkins", systems[0].system_type.value)

    def tests_validator_validate_environments_no_envs(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["env_name"] = Mock()
        self.ci_args["env_name"].value = ["unknown"]
        self.ci_args["system_type"] = Mock()
        self.ci_args["system_type"].value = ["jenkins"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        self.assertRaises(NoValidEnvironment,
                          validator.validate_environments,
                          original_envs)

    def tests_validator_validate_environments_no_systems(self):
        """Testing Validator validate_environment method."""
        self.orchestrator.config.data = self.config
        self.orchestrator.create_ci_environments()
        self.ci_args["system_name"] = Mock()
        self.ci_args["system_name"].value = ["unknown"]

        validator = Validator(self.ci_args)
        original_envs = self.orchestrator.environments

        self.assertRaises(NoValidSystem,
                          validator.validate_environments,
                          original_envs)
