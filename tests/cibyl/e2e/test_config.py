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

from tests.cibyl.e2e.containers.httpd import HTTPDContainer


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
