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
import builtins
import sys
from unittest.mock import Mock

from cibyl.cli.main import main
from tests.e2e.containers.httpd import HTTPDContainer
from tests.e2e.fixtures import EndToEndTest


class TestConfig(EndToEndTest):
    """Test for configuration loading.
    """

    def test_config_on_url(self):
        """Checks that a configuration file can be downloaded from a host.
        """
        with HTTPDContainer() as httpd:
            sys.argv = [
                '',
                '--config', f'{httpd.url}/jenkins.yaml'
            ]

            builtins.input = Mock()
            builtins.input.return_value = 'y'

            main()

            # Look for some keys that indicate that it is the desired file
            self.assertIn('test_environment', self.output)
            self.assertIn('test_system', self.output)
