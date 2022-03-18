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
from cibyl.cli.argument import Argument
from cibyl.models.model import Model

# pylint: disable=no-member


class Node(Model):
    """
    This a model for your typical node used on Openstack deployment.
    """
    # To be implemented in future PR

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--name', arg_type=str,
                          description="Node name")]
        },
        'node_id': {
            'attr_type': str,
            'arguments': [Argument(name='--id', arg_type=str,
                          description="Id provided for the node")]
        },
        'status': {
            'attr_type': str,
            'arguments': [Argument(name='--status', arg_type=str,
                          description="Active or inactive status on node")]
        },
        'time_created': {
            'attr_type': str,
            'arguments': [Argument(name='--time-created', arg_type=str,
                          description="Time stamp when node was created")]
        },
        'role': {
            'attr_type': str,
            'arguments': [Argument(name='--role', arg_type=str,
                          description="Role for the node")]
        }
    }

    def __init__(self, name: str, node_id: str,
                 status: str, time_created: str, role: str):
        super().__init__({'name': name, 'node_id': node_id, 'role': role,
                           'status': status, 'time_created': time_created})

    def __str__(self, indent=0):
        info = f'Node name: {self.name.value}'
        if self.status:
            info += f'\n Status: {self.status.value.__str__(indent + 2)}'
        if self.time_created:
            info += f'\n Time created: {self.time_created.value.__str__(indent + 2)}'
        if self.role:
            info += f'\n Role: {self.role.value.__str__(indent + 2)}'
        return info
