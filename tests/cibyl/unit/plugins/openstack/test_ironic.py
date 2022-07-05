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

from cibyl.plugins.openstack.ironic import Ironic


class TestOpenstackIronic(TestCase):
    """Test openstack ironic model."""
    def setUp(self):
        self.ironic_inspector = "true"
        self.cleaning_network = "true"
        self.second_ironic = Ironic(ironic_inspector=self.ironic_inspector,
                                    cleaning_network=self.cleaning_network)
        self.ironic = Ironic()

    def test_merge_method(self):
        """Test merge method of Ironic class."""
        self.assertIsNone(self.ironic.ironic_inspector.value)
        self.ironic.merge(self.second_ironic)

        self.assertEqual(self.ironic_inspector,
                         self.ironic.ironic_inspector.value)
        self.assertEqual(self.cleaning_network,
                         self.ironic.cleaning_network.value)
