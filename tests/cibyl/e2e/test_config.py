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
import sys
from unittest import TestCase

from cibyl.cli.main import main
from tests.cibyl.e2e.containers.httpd import HTTPDContainer
from tests.cibyl.e2e.fixtures import EndToEndTest


class TestConfig(TestCase):
    """Tests for configuration loading.
    """

    def test_config_on_url(self):
        """Checks that a configuration file can be downloaded from a host.
        """
        with HTTPDContainer() as httpd:
            command = [
                'cibyl', '--config', f'{httpd.url}/jenkins.yaml',
                '-f', 'text'
            ]

            stdout, _, _ = httpd.run('cibyl', command)

            # Look for some keys that indicate that it is the desired file
            self.assertIn('test_environment', stdout)
            self.assertIn('test_system', stdout)


class TestSchema(EndToEndTest):
    """Tests configuration files against their schema.
    """

    def test_disabled_configuration(self):
        """Checks that the example for a disabled system gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/disabled_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_jenkins_1\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_elasticsearch_configuration(self):
        """Checks that the example for an elasticsearch source gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/elasticsearch_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_jenkins\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_full_configuration(self):
        """Checks that the example for a full configuration gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/full_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_jenkins_1\n'
            '  System: production_jenkins_2\n'
            '  System: production_zuul\n'
            'Environment: staging\n'
            '  System: staging_jenkins\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_jjb_configuration(self):
        """Checks that the example for a jjb source gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/jjb_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_jenkins\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_minimal_configuration(self):
        """Checks that the example for a minimal configuration gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/minimal_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_jenkins\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_zuul_configuration(self):
        """Checks that the example for a zuul source gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/zuul_api_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_zuul\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_zuuld_local_configuration(self):
        """Checks that the example for a zuuld source gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/'
                  'zuul_definitions_local_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_zuul\n'
        )

        self.assertEqual(expected, self.stdout)

    def test_zuuld_remote_configuration(self):
        """Checks that the example for a zuuld source gets a pass.
        """
        sys.argv = [
            'cibyl',
            '-f', 'text',
            '-c', 'docs/source/config_samples/'
                  'zuul_definitions_remote_configuration.yaml'
        ]

        main()

        expected = (
            'Environment: production\n'
            '  System: production_zuul\n'
        )

        self.assertEqual(expected, self.stdout)
