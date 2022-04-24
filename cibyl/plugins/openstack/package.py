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

# pylint: disable=no-member


class Package(Model):
    """ Model for packages found on Openstack node."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'origin': {
            'attr_type': str,
            'arguments': [Argument(name='--package-origin', arg_type=str,
                                   nargs="*", func="get_deployment",
                                   description="Package origin")]
        }
    }

    def __init__(self, name: str, origin: str = None):
        super().__init__({'name': name, 'origin': origin})

    def merge(self, other):
        """Merge the information of two package objects representing the
        same package.

        :param other: The Package object to merge
        :type other: :class:`.Package`
        """
        if not self.origin.value:
            self.origin.value = other.origin.value
