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
        }
    }

    def __init__(self, release: float, infra_type: str,
                 nodes: List[Node], services: List[Service]):
        super().__init__({'release': release, 'infra_type': infra_type,
                          'nodes': nodes, 'services': services})

    def __str__(self):
        info = f'Release: {self.release.value}'
        info += f'Infra type: {self.infra_type.value} \n'
        for node in self.nodes:
            info += node.__str__()
        if self.service:
            info += f'\n Service: {self.service.value}'
        return info
