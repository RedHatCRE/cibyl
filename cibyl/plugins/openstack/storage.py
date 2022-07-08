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

from cibyl.cli.argument import Argument
from cibyl.models.model import Model

# pylint: disable=no-member


class Storage(Model):
    """Storage properties of an openstack deployment"""

    API = {
        'cinder_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--cinder-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Cinder backend used in the "
                                               "deployment")]
        }
    }

    def __init__(self, cinder_backend: Optional[str] = None):
        super().__init__({'cinder_backend': cinder_backend})

    def merge(self, other: 'Storage'):
        """Merge the information of two deployment objects representing the
        same deployment.

        :param other: The Deployment object to merge
        """
        if not self.cinder_backend.value:
            self.cinder_backend.value = other.cinder_backend.value
