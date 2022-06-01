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
# pylint: disable=no-member
from cibyl.models.model import Model


class Stage(Model):
    """General model for a build stage

    @DynamicAttrs: Contains attributes added on runtime.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'status': {
            'attr_type': str,
            'arguments': []
        },
        'duration': {
            'attr_type': int,
            'arguments': [],
        }
    }

    def __init__(self, name: str, status: str = None,
                 duration: int = None):
        if status is not None:
            status = status.upper()
        super().__init__({'name': name, 'status': status,
                          'duration': duration})

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value

    def merge(self, other):
        """Merge the information of two build objects representing the same
        build.

        :param other: The Build object to merge
        :type other: :class:`.Build`
        """
        if not self.status.value:
            self.status.value = other.status.value
