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

from cibyl.config import AppConfig
from cibyl.exceptions.config import CHECK_DOCS_MSG, NonSupportedSystemKey
from cibyl.orchestrator import Orchestrator
from tests.cibyl.utils import OpenstackPluginWithJobSystem


class TestOrchestratorSetup(TestCase):
    """Setup orchestrator tests that can be reused in different test
    classes."""

    def setUp(self):
        self.orchestrator = Orchestrator()

        self.missing_envs_config = {'environments': {}}

        self.missing_system_type_config = {
            'environments': {
                'env1': 'system'}}

        self.valid_single_env_config_data = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins',
                        'sources': {}}}}}

        self.valid_multiple_envs_config_data = {
            'environments': {
                'env3': {
                    'system3': {
                        'system_type': 'jenkins',
                        'sources': {}},
                    'system4': {
                        'system_type': 'zuul',
                        'sources': {}}
                },
                'env4': {
                    'system1': {
                        'system_type': 'zuul',
                        'sources': {}}
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
        self.valid_env_sources_disabled = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins',
                        'sources': {
                            'elasticsearch': {
                                'driver': 'elasticsearch',
                                'url': ''
                            },
                            'jenkins2': {
                                'driver': 'jenkins',
                                'enabled': False,
                                'url': ''
                            }
                        }}}}}

        self.all_sources_enabled = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins',
                        'sources': {
                            'elasticsearch': {
                                'driver': 'elasticsearch',
                                'enabled': False,
                                'url': ''
                            },
                            'jenkins2': {
                                'driver': 'jenkins',
                                'enabled': False,
                                'url': ''
                            },
                            'zuul': {
                                'driver': 'zuul',
                                'enabled': False,
                                'url': ''
                            },
                            'jjb': {
                                'driver': 'jenkins_job_builder',
                                'enabled': False,
                                'repos': {}
                            },
                            'zuuld': {
                                'driver': 'zuul.d',
                                'enabled': False,
                                'repos': {}
                                }}}}}}


class TestOrchestrator(TestOrchestratorSetup):
    """Test Orchestrator methods."""
    def test_orchestrator_config(self):
        """Testing Orchestrator config attribute and method"""
        self.assertTrue(hasattr(self.orchestrator, 'config'))

    def test_orchestrator_create_ci_environments(self):
        """Testing orchestrator environments creation."""
        # Single environment configuration
        self.orchestrator.config = AppConfig(
            data=self.valid_single_env_config_data)
        self.orchestrator.environments = []
        self.orchestrator.create_ci_environments()
        self.assertEqual(len(self.orchestrator.environments), 1)
        self.assertEqual(self.orchestrator.environments[0].name.value, 'env1')
        self.assertEqual(
            len(self.orchestrator.environments[0].systems.value), 1)
        self.assertEqual(
            self.orchestrator.environments[0].systems[0].name.value, 'system1')

        # Multiple environments configuration
        self.orchestrator.config = AppConfig(
            data=self.valid_multiple_envs_config_data)
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

    def test_extend_parser(self):
        """Test that extend_parser creates the right cli arguments for a single
        jenkins system."""
        self.orchestrator.config = AppConfig(
            data=self.valid_single_env_config_data)
        self.orchestrator.create_ci_environments()
        for env in self.orchestrator.environments:
            self.orchestrator.extend_parser(attributes=env.API)
        self.orchestrator.parser.parse(["--jobs", "--builds"])
        self.assertTrue("jobs" in self.orchestrator.parser.ci_args)
        self.assertTrue("builds" in self.orchestrator.parser.ci_args)
        self.assertEqual(self.orchestrator.parser.ci_args["jobs"].level, 2)
        self.assertEqual(self.orchestrator.parser.ci_args["builds"].level, 3)

    def test_extend_parser_zuul_system(self):
        """Test that extend_parser creates the right cli arguments for multiple
        environments and systems."""
        self.orchestrator.config = AppConfig(
            data=self.valid_multiple_envs_config_data)
        self.orchestrator.create_ci_environments()
        for env in self.orchestrator.environments:
            self.orchestrator.extend_parser(attributes=env.API)
        self.orchestrator.parser.parse([
            "--jobs", "--builds", "--tenants", "--projects", "--pipelines"
        ])
        self.assertTrue("tenants" in self.orchestrator.parser.ci_args)
        self.assertTrue("jobs" in self.orchestrator.parser.ci_args)
        self.assertTrue("builds" in self.orchestrator.parser.ci_args)
        self.assertEqual(self.orchestrator.parser.ci_args["tenants"].level, 2)
        self.assertEqual(self.orchestrator.parser.ci_args["projects"].level, 3)
        self.assertEqual(
            self.orchestrator.parser.ci_args["pipelines"].level, 4)
        self.assertEqual(self.orchestrator.parser.ci_args["jobs"].level, 5)
        self.assertEqual(self.orchestrator.parser.ci_args["builds"].level, 6)

    def test_validate_environments(self):
        """Test that validate_environments filters the environments."""
        self.orchestrator.config = AppConfig(
            data=self.valid_multiple_envs_config_data)
        self.orchestrator.create_ci_environments()
        self.orchestrator.parser.ci_args["systems"] = Mock()
        self.orchestrator.parser.ci_args["systems"].value = ["system1"]
        self.orchestrator.validate_environments()
        self.assertEqual(len(self.orchestrator.environments), 1)
        env = self.orchestrator.environments[0]
        self.assertEqual(len(env.systems.value), 1)
        self.assertEqual(env.name.value, 'env4')
        self.assertEqual(env.systems[0].name.value, 'system1')

    def test_not_supported_system_key_jobs_system(self):
        """Test that a NonSupportedSystemKey is raised if the configuration
        contains invalid parameters for a jobs system."""
        config = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'jenkins',
                        'sources': {},
                        'tenants': 'tenant'}}}}
        self.orchestrator.config = AppConfig(data=config)
        msg = "The following key in jenkins system type is not supported:"
        msg += f" tenants\n\n{CHECK_DOCS_MSG}"
        with self.assertRaises(NonSupportedSystemKey, msg=msg):
            self.orchestrator.create_ci_environments()

    def test_not_supported_system_key_zuul_system(self):
        """Test that a NonSupportedSystemKey is raised if the configuration
        contains invalid parameters for a zuul system."""
        config = {
            'environments': {
                'env1': {
                    'system1': {
                        'system_type': 'zuul',
                        'sources': {},
                        'non-existing': 'tenant'}}}}
        self.orchestrator.config = AppConfig(data=config)
        msg = "The following key in jenkins system type is not supported:"
        msg += f" non-existing\n\n{CHECK_DOCS_MSG}"
        with self.assertRaises(NonSupportedSystemKey, msg=msg):
            self.orchestrator.create_ci_environments()

    def test_create_envs_with_sources_enabled_attribute(self):
        """Test that all sources support the enabled parameter."""
        self.orchestrator.config = AppConfig(data=self.all_sources_enabled)
        self.orchestrator.create_ci_environments()
        env = self.orchestrator.environments[0]
        system = env.systems[0]
        sources = system.sources.value
        self.assertEqual(len(sources), 5)
        for source in sources:
            self.assertFalse(source.enabled)


class TestOrchestratorArgumentsFiltering(TestOrchestratorSetup):
    """Test the sort_and_filter_args method of the orchestrator."""

    def setUp(self):
        super().setUp()
        self.orchestrator.config = AppConfig(
            data=self.valid_single_env_config_data)
        self.orchestrator.create_ci_environments()
        for env in self.orchestrator.environments:
            self.orchestrator.extend_parser(attributes=env.API)

    def test_jobs_builds(self):
        """Test that sort_and_filter_args handles properly the case with two
        arguments with different func attributes."""
        self.orchestrator.parser.parse(["--jobs", "--builds"])
        args = self.orchestrator.sort_and_filter_args()
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].name, "builds")
        self.assertEqual(args[1].name, "jobs")

    def test_filter_args_with_no_func(self):
        """Test that sort_and_filter_args handles properly the case with two
        arguments with different func attributes."""
        self.orchestrator.parser.parse(["--systems", "", "--envs", ""])
        args = self.orchestrator.sort_and_filter_args()
        self.assertEqual(len(args), 0)

    def test_multiple_builds_arguments(self):
        """Test that sort_and_filter_args handles properly the case with two
        arguments that should query get_builds."""
        self.orchestrator.parser.parse(["--jobs", "--builds",
                                        "--build-status"])
        args = self.orchestrator.sort_and_filter_args()
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].name, "builds")
        self.assertEqual(args[1].name, "jobs")

    def test_multiple_builds_tests_arguments(self):
        """Test that sort_and_filter_args handles properly the case with two
        arguments that should query get_builds and two that should query
        get_tests."""
        self.orchestrator.parser.parse(["--jobs", "--builds",
                                        "--build-status", "--tests",
                                        "--test-result"])
        args = self.orchestrator.sort_and_filter_args()
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0].name, "tests")
        self.assertEqual(args[1].name, "builds")
        self.assertEqual(args[2].name, "jobs")


class TestArgumentsFilteringOpenstack(OpenstackPluginWithJobSystem,
                                      TestOrchestratorArgumentsFiltering):
    """Test the sort_and_filter_args method of the orchestrator."""

    def test_multiple_deployment_arguments_different_level(self):
        """Test that sort_and_filter_args handles properly the case with many
        arguments that should query get_deployment with different levels."""
        self.orchestrator.parser.parse(["--jobs", "--ip-version",
                                        "--packages", '--release'])
        args = self.orchestrator.sort_and_filter_args()
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].name, "packages")
        self.assertEqual(args[1].name, "jobs")
