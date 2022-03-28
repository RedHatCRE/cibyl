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

from cibyl.models.ci.environment import Environment
from cibyl.plugins import extend_models


class TestOpenstackPlugin(TestCase):
    """Test OpenStack plugin"""

    def test_extend_models(self):
        """Test extend_models method"""
        self.assertIsNone(extend_models("openstack"))
        environment = Environment("test")
        environment.add_system(name="test", system_type='jenkins')
        self.assertIn(
            'deployment',
            environment.systems[0].jobs.attr_type.API)
