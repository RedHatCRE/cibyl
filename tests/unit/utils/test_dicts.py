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
from unittest import TestCase

from cibyl.utils.dicts import subset


class TestSubset(TestCase):
    def test_subset_is_generated(self):
        """Checks that this is capable of creating a dictionary from another.
        """
        original = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        keys = ['a', 'c']

        self.assertEqual(
            {
                'a': 1,
                'c': 3
            },
            subset(original, keys)
        )
