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
from typing import Dict

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.model import Model
from cibyl.plugins.openstack.package import Package

# pylint: disable=no-member


class Container(Model):
    """Model for containers found on Openstack nodes."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'image': {
            'attr_type': str,
            'arguments': [Argument(name='--container-image', arg_type=str,
                                   nargs="*", func="get_deployment",
                                   description="Container image")]
        },
        'packages': {
            'attr_type': Package,
            'attribute_value_class': AttributeDictValue,
            'arguments': []
        }
    }

    def __init__(self, name: str, image: str = None,
                 packages: Dict[str, Package] = None):
        super().__init__({'name': name, 'image': image, 'packages': packages})

    def add_package(self, package: Package):
        """Add a package to the container.

        :param package: Package to add to the deployment
        :type package: Package
        """
        package_name = package.name.value
        if package_name in self.packages:
            self.packages[package_name].merge(package)
        else:
            self.packages[package_name] = package

    def merge(self, other):
        """Merge the information of two container objects representing the
        same container.

        :param other: The Container object to merge
        :type other: :class:`.Container`
        """
        if not self.image.value:
            self.image.value = other.image.value
        for package in other.packages.values():
            self.add_package(package)
