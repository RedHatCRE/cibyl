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
from cibyl.utils.colors import Colors

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
        indent_space = indent*' '
        info = f'{indent_space}'
        info += Colors.blue('Node name: ') + f'{self.name.value}'
        if self.role.value and verbosity > 0:
            info += f'\n{indent_space}  ' + Colors.blue('Role: ')
            info += f'{self.role}'
        if self.containers.value:
            for container in self.containers:
                info += f'\n{indent_space}  ' + Colors.blue('Container: ')
                info += f'{container.__str__(indent)}'
        if self.packages.value:
            for package in self.packages:
                info += f'\n{indent_space}  ' + Colors.blue('Package: ')
                info += f'{package.__str__(indent)}'
        return info
