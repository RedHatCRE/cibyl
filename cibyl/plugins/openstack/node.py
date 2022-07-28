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
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.package import Package

# pylint: disable=no-member


class Node(Model):
    """
    This a model for your typical node used on Openstack deployment.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'role': {
            'attr_type': str,
            'arguments': [Argument(name='--role', arg_type=str,
                                   description="Role for the node")]
        },
        'containers': {
            'attr_type': Container,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--containers', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Containers on the node")]
        },
        'packages': {
            'attr_type': Package,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--packages', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Packages in the node")]
        }
    }

    def __init__(self, name: str, role: str = None,
                 containers: Dict[str, Container] = None,
                 packages: Dict[str, Package] = None):
        super().__init__({'name': name, 'role': role, 'containers': containers,
                          'packages': packages})

    def add_container(self, container: Container):
        """Add a container to the node.

        :param container: Container to add to the node
        :type container: Container
        """
        container_name = container.name.value
        if container_name in self.containers:
            self.containers[container_name].merge(container)
        else:
            self.containers[container_name] = container

    def add_package(self, package: Package):
        """Add a package to the node.

        :param package: Package to add to the node
        :type package: Package
        """
        package_name = package.name.value
        if package_name in self.packages:
            self.packages[package_name].merge(package)
        else:
            self.packages[package_name] = package

    def merge(self, other):
        """Merge the information of two node objects representing the
        same node.

        :param other: The Node object to merge
        :type other: :class:`.Node`
        """
        if not self.role.value:
            self.role.value = other.role.value
        for package in other.packages.values():
            self.add_package(package)
        for container in other.containers.values():
            self.add_container(container)
