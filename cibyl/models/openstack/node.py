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

# flake8: noqa from cibyl.cli.argument import Argument
# flake8: noqa from cibyl.models.attribute import AttributeListValue
from typing import Dict

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.model import Model
from cibyl.models.openstack.container import Container
from cibyl.models.openstack.package import Package

# pylint: disable=no-member


class Node(Model):
    """
    This a model for your typical node used on Openstack deployment.
    """

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--node-name', arg_type=str,
                          description="Node name")]
        },
        'role': {
            'attr_type': str,
            'arguments': [Argument(name='--role', arg_type=str,
                          description="Role for the node")]
        },
        'containers': {
            'attr_type': Container,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--node-containers', arg_type=str,
                          nargs='*', description="Containers on the node")]
        },
        'packages': {
            'attr_type': Package,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--node-packages', arg_type=str,
                          nargs='*', description="Packages in the node")]
        }
    }

    def __init__(self, name: str, role: str = None,
                 containers: Dict[str, Container] = None,
                 packages: Dict[str, Package] = None):
        super().__init__({'name': name, 'role': role, 'containers': containers,
                          'packages': packages})

    def __str__(self, indent=2, verbosity=0):
        info = f'Node name: {self.name.value}'
        if self.role.value and verbosity > 0:
            info += f'\n Role: {self.role.value.__str__(indent)}'
        if self.containers.value:
            for container in self.containers:
                info += f'Container: {container.__str__(indent)}'
        if self.packages.value:
            for package in self.packages:
                info += f'Package: {package.__str__(indent)}'
        if self.packages.value:
            for package in self.packages:
                info += f'Package: {self.package.value}'
        return info
