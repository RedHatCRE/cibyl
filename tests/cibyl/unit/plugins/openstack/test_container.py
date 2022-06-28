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
from cibyl.plugins.openstack.package import Package


class TestOpenstackContainer(TestCase):
    """Test openstack container model."""
    def setUp(self):
        self.name = 'test-container'
        self.image = 'image'
        self.packages = {'package': Package('package')}
        self.container = Container(self.name, packages=self.packages)
        self.packages2 = {'package': Package('package', 'rhos-release'),
                          'new-package': Package('new-package')}
        self.container2 = Container(self.name, self.image,
                                    packages=self.packages2)

    def test_merge(self):
        """Test Container merge method."""
        self.container.merge(self.container2)
        self.assertEqual(self.image, self.container.image.value)
        self.assertEqual(2, len(self.container.packages))
        package = self.container.packages['package']
        self.assertEqual(package.name.value, 'package')
        self.assertEqual(package.origin.value, 'rhos-release')
        new_package = self.container.packages['new-package']
        self.assertEqual(new_package.name.value, 'new-package')
