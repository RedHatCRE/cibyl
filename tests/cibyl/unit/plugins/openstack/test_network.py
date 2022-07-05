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

from cibyl.plugins.openstack.network import Network


class TestOpenstackNetwork(TestCase):
    """Test openstack deployment model."""
    def setUp(self):
        self.ip_version = "4"
        self.network_backend = "vxlan"
        self.dvr = "true"
        self.tls_everywhere = "false"
        self.ml2_driver = "ovn"
        self.security_group = "native ovn"
        self.second_network = Network(ip_version=self.ip_version,
                                      network_backend=self.network_backend,
                                      dvr=self.dvr, ml2_driver=self.ml2_driver,
                                      tls_everywhere=self.tls_everywhere,
                                      security_group=self.security_group)
        self.network = Network()

    def test_merge_method(self):
        """Test merge method of Network class."""
        self.assertIsNone(self.network.ip_version.value)
        self.network.merge(self.second_network)

        self.assertEqual(self.ip_version, self.network.ip_version.value)
        self.assertEqual(self.network_backend,
                         self.network.network_backend.value)
        self.assertEqual(self.dvr, self.network.dvr.value)
        self.assertEqual(self.tls_everywhere,
                         self.network.tls_everywhere.value)
        self.assertEqual(self.ml2_driver, self.network.ml2_driver.value)
        self.assertEqual(self.security_group,
                         self.network.security_group.value)
