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

import cibyl.config
from cibyl.config import Config


class TestConfig(TestCase):
    """Test cases for the 'Config' class.
    """

    def test_contents_are_loaded(self):
        """Checks that the contents of the loaded file are made available by
        the class.
        """
        file = 'path/to/config/file'
        yaml = {
            'node_a': {
                'name': 'Test',
                'host': 'test_host'
            }
        }

        cibyl.config.yaml.parse = Mock()
        cibyl.config.yaml.parse.return_value = yaml

        config = Config()
        config.load(file)

        cibyl.config.yaml.parse.assert_called_with(file)

        self.assertEqual(config, yaml)
