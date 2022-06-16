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

from cibyl.models.model import Model

# pylint: disable=no-member


class Service(Model):
    """Model for services found on Openstack deployment."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'configuration': {
            'attr_type': dict,
            'arguments': []
        }
    }

    def __init__(self, name: str, configuration: Dict[str, str] = None):
        super().__init__({'name': name, 'configuration': configuration})

    def merge(self, other):
        """Merge two Service objects representing the same service."""
        self.configuration.value.update(other.configuration.value)
