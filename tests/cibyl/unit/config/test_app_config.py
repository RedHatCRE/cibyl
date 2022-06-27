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

import cibyl.exceptions.config as conf_exc
from cibyl.config import AppConfig


class TestAppConfig(TestCase):
    """Test cases for the 'AppConfig' class."""

    def test_missing_environments_in_app_config(self):
        data = {'environments': {}}
        self.config = AppConfig(data=data)
        with self.assertRaises(conf_exc.MissingEnvironments):
            self.config.verify()

    def test_missing_systems_in_app_config(self):
        data = {'environments': 'env1'}
        self.config = AppConfig(data=data)
        with self.assertRaises(conf_exc.MissingSystems):
            self.config.verify()

    def test_missing_system_type_in_app_config(self):
        data = {'environments':
                {'env1': 'system1'}}
        self.config = AppConfig(data=data)
        with self.assertRaises(conf_exc.MissingSystemType):
            self.config.verify()

    def test_missing_system_sources_in_app_config(self):
        data = {'environments':
                {'env1':
                 {'system1':
                  {'foo': 'bar'}}}}
        self.config = AppConfig(data=data)
        with self.assertRaises(conf_exc.MissingSystemSources):
            self.config.verify()
