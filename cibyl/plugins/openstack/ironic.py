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
from typing import Optional

from cibyl.models.model import Model

# pylint: disable=no-member


class Ironic(Model):
    """Ironic-related properties of an openstack deployment"""

    API = {
        'cleaning_network': {
            'arguments': []
        },
        'ironic_inspector': {
            'arguments': []
        }
    }

    def __init__(self, ironic_inspector: Optional[str] = None,
                 cleaning_network: Optional[str] = None):
        super().__init__({'ironic_inspector': ironic_inspector,
                          'cleaning_network': cleaning_network})

    def merge(self, other: 'Ironic'):
        """Merge the information of two deployment objects representing the
        same deployment.

        :param other: The Deployment object to merge
        :type other: :class:`.Deployment`
        """
        if not self.ironic_inspector.value:
            self.ironic_inspector.value = other.ironic_inspector.value
        if not self.cleaning_network.value:
            self.cleaning_network.value = other.cleaning_network.value
