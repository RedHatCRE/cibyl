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
from typing import List

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeListValue
from cibyl.models.model import Model
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.service import Service
from cibyl.utils.colors import Colors

# pylint: disable=no-member


class Deployment(Model):
    """Openstack deployment model"""

    API = {
        'release': {
            'attr_type': float,
            'arguments': [Argument(name='--release', arg_type=float,
                                   description="Deployment release version")]
        },
        'infra_type': {
            'attr_type': str,
            'arguments': [Argument(name='--infra-type', arg_type=str,
                                   description="Infra type")]
        },
        'nodes': {
            'attr_type': Node,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--nodes', arg_type=str,
                                   nargs='*',
                                   description="Nodes on the deployment")]
        },
        'services': {
            'attr_type': Service,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--services', arg_type=str,
                                   nargs='*',
                                   description="Services in the deployment")]
        },
        'ip_version': {
            'attr_type': str,
            'arguments': [Argument(name='--ip-version', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Ip version used in the "
                                   "deployment")]
            },
        'topology': {
            'attr_type': str,
            'arguments': [Argument(name='--topology', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Topology used in the "
                                   "deployment")]
            }
    }

    def __init__(self, release: float, infra_type: str,
                 nodes: List[Node], services: List[Service],
                 ip_version: str = None, topology: str = None):
        super().__init__({'release': release, 'infra_type': infra_type,
                          'nodes': nodes, 'services': services,
                          'ip_version': ip_version, 'topology': topology})

    def __str__(self, indent=0, verbosity=0):
        indent_space = indent*' '
        info = f'{indent_space}' + Colors.blue("Release: ")
        info += f'{self.release.value}'

        info += f'\n{indent_space}' + Colors.blue('Infra type: ')
        info += f'{self.infra_type.value}'
        for node in self.nodes:
            info += f'\n{indent_space}  '
            info += f'{node.__str__(indent=indent+2, verbosity=verbosity)}'
        if self.services.value:
            info += f'\n{indent_space}' + Colors.blue('Service: ')
            info += f'{self.services.value}'
        if self.ip_version.value:
            info += f'\n{indent_space}' + Colors.blue('IP version: ')
            info += f'{self.ip_version}'
        if self.topology.value:
            info += f'\n{indent_space}' + Colors.blue('Topology: ')
            info += f'{self.topology}'
        return info
