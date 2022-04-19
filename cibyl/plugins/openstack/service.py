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
from cibyl.models.model import Model
from cibyl.utils.colors import Colors

# pylint: disable=no-member


class Service(Model):
    """Model for services found on Openstack deployment."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--service-name', arg_type=str,
                          description="Service name")]
        },
        'configuration': {
            'attr_type': dict,
            'arguments': [Argument(name='--service-config', arg_type=str,
                          description="Service configuration")]
        }
    }

    def __init__(self, name: str, configuration: Dict[str, str] = None):
        super().__init__({'name': name, 'configuration': configuration})

    def __str__(self, indent=2, verbosity=0):
        indent_space = indent*' '
        info = f'{indent_space}'
        info += Colors.blue('Service name: ') + f'{self.name.value}'
        if self.configuration.value and verbosity > 0:
            for parameter, value in self.configuration.value.items():
                info += f'\n{indent_space}  ' + Colors.blue(f'{parameter}: ')
                info += f'{value}'
        return info

    def merge(self, other):
        """Merge two Service objects representing the same service."""
        self.configuration.value.update(other.configuration.value)
