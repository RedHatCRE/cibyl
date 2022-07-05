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

from typing import Optional, Set

from cibyl.models.model import Model

# pylint: disable=no-member


class TestCollection(Model):
    """ Model for a collection of tests run in an Openstack deployment."""

    API = {
        'tests': {
            'attr_type': set,
            'arguments': []
        },
        'setup': {
            'attr_type': str,
            'arguments': []
        }
    }

    def __init__(self, tests: Optional[Set[str]] = None,
                 setup: Optional[str] = None):
        if tests is None:
            tests = set()
        super().__init__({'tests': tests, 'setup': setup})

    def merge(self, other):
        """Merge the information of two TestCollection objects representing the
        same collection of tests.

        :param other: The TestCollection object to merge
        :type other: :class:`.TestCollection`
        """
        if not self.setup.value:
            self.setup.value = other.setup.value
        self.tests.value.update(other.tests.value)
