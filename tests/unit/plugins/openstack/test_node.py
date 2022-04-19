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

from cibyl.plugins.openstack.node import Node


class TestOpenstackNode(TestCase):
    """Test openstack node model."""
    def setUp(self):
        self.name = 'controller-0'
        self.role = 'controller'
        self.node = Node(self.name, self.role)

    def test_str_method(self):
        """Test that the string representation of Node works."""
        node_str = self.node.__str__(verbosity=1)
        self.assertIn("Node name:", node_str)
        self.assertIn(self.name, node_str)
        self.assertIn("Role: ", node_str)
        self.assertIn(self.role, node_str)
