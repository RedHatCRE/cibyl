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
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.zuul.job import Job as ZuulJob
from cibyl.plugins import enable_plugins
from cibyl.plugins.openstack import Plugin
from tests.cibyl.utils import RestoreAPIs


class TestPlugin(RestoreAPIs):
    """Test Plugins mechanism"""

    def test_enable_plugins(self):
        """Test enable_plugins method"""
        # check that the openstack plugin returns only a list with one element,
        # the function to create the spec subparser
        self.assertEqual(len(enable_plugins(["openstack"])), 1)

    def test_missing_plugin(self):
        """Test enable_plugins method with a non-existing plugin."""
        self.assertRaises(MissingPlugin,
                          enable_plugins,
                          ["nonExistingPlugin"])

    def test_extends_jenkins_job(self):
        """Checks that the plugin extends the base job model.
        """
        plugin = Plugin()
        plugin.extend_models()

        # Plugin's of model are empty
        self.assertIn('deployment', Job.plugin_attributes)

    def test_extends_variant(self):
        """Checks that the plugin extends the zuul variant model.
        """
        plugin = Plugin()
        plugin.extend_models()

        # Plugin's of model are empty
        self.assertIn('deployment', ZuulJob.Variant.plugin_attributes)

    def test_do_not_extend_zuul_job(self):
        """Checks that the plugin does not extend a model it should not do.
        """
        plugin = Plugin()
        plugin.extend_models()

        # Plugin's of model are empty
        self.assertFalse(ZuulJob.plugin_attributes)
