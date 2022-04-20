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

from cibyl.plugins.openstack.service import Service


class TestOpenstackService(TestCase):
    """Test openstack service model."""
    def setUp(self):
        self.name = 'test-service'
        self.config = {'option1': 'true'}
        self.service = Service(self.name, self.config)

    def test_str_method(self):
        """Test that the string representation of Service works."""
        service_str = self.service.__str__(verbosity=1)
        self.assertIn("Service name:", service_str)
        self.assertIn(self.name, service_str)
        self.assertIn("option1:", service_str)
        self.assertIn("true", service_str)
