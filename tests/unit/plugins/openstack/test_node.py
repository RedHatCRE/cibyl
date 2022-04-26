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

from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package


class TestOpenstackNode(TestCase):
    """Test openstack node model."""
    def setUp(self):
        self.name = 'test-node'
        self.role = 'test'
        self.packages = {'package': Package('package')}
        self.containers = {'container': Container('container')}
        self.node = Node(self.name, packages=self.packages,
                         containers=self.containers)
        self.packages2 = {'package': Package('package', 'rhos-release'),
                          'new-package': Package('new-package')}
        self.containers2 = {'container': Container('container', image='image'),
                            'new-container': Container('new-container',
                                                       'image')}
        self.node2 = Node(self.name, self.role, packages=self.packages2,
                          containers=self.containers2)

    def test_merge(self):
        """Test Node merge method."""
        self.node.merge(self.node2)
        self.assertEqual(self.role, self.node.role.value)
        self.assertEqual(2, len(self.node.packages))
        package = self.node.packages['package']
        self.assertEqual(package.name.value, 'package')
        self.assertEqual(package.origin.value, 'rhos-release')
        new_package = self.node.packages['new-package']
        self.assertEqual(new_package.name.value, 'new-package')
        self.assertEqual(2, len(self.node.containers))
        container = self.node.containers['container']
        self.assertEqual(container.name.value, 'container')
        self.assertEqual(container.image.value, 'image')
        new_container = self.node.containers['new-container']
        self.assertEqual(new_container.image.value, 'image')
