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

from cibyl.cli.argument import Argument
from cibyl.models.model import Model
from cibyl.models.attribute import AttributeListValue


class Deployment(Model):
    """Openstack deployment model"""

    API = { 
        'release': {
            'attr_type': float,
            'arguments': [Argument(name='--release', arg_type=float,
                description="Deployment release number")]
        },                                                                                        
        'infra_type': {
            'attr_type': str,
            'arguments': [Argument(name='--infra-type', arg_type=str,
                description="Infra type")]
        },
        'nodes': {
            'attr_type': str,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--nodes', arg_type=str,
                description="Nodes on the deployment")]
        },
        'service': {
            'attr_type': Service,  

            # Not sure if I should go with building another 
            # model for the service attribute or go with
            # just a AttributeListValue. Thoughts?

            'arguments': [Argument(name='--configuration', arg_type=str,
                description= "Services in the deployment")]
        }
    }

    def __init__(self, name: str, release:float, infra_type: str):
        super().__init__({'release': release, 'infra_type': infra_type,
            'nodes': nodes, 'service': configuration})

    def __str__(self):
        info = f'Release: {self.release} \n Infra type: {infra_type} \n'
        for node in self.nodes:
            info += node.__str__()
        return info
        
