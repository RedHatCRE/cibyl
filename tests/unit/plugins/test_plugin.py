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

from cibyl.exceptions.plugin import MissingPlugin
from cibyl.plugins import enable_plugins
from tests.utils import RestoreAPIs


class TestPlugin(RestoreAPIs):
    """Test Plugins mechanism"""

    def test_enable_plugins(self):
        """Test enable_plugins method"""
        self.assertIsNone(enable_plugins(["openstack"]))

    def test_missing_plugin(self):
        """Test enable_plugins method with a non-existing plugin."""
        self.assertRaises(MissingPlugin,
                          enable_plugins,
                          ["nonExistingPlugin"])
