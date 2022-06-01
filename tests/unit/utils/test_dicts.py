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

from cibyl.utils.dicts import chunk_dictionary_into_lists, nsubset, subset


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


class TestNSubset(TestCase):
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
                'b': 2
            },
            nsubset(original, keys)
        )


class TestChunkDictionaryResult(TestCase):
    def test_chunk_dictionary_result(self):
        """Checks that this is able to create a list with sub lists
        as chunk mode using the keys of a dictionary and the quantity
        of each one of the sub lists
        """
        # Create a dictionary of 500 keys:
        dictionary = {k: k for k in range(500)}
        sublist_size = 200
        lists = chunk_dictionary_into_lists(
            dictionary,
            sublist_size
        )
        # 500 / 200 = 2.5 so we should have:
        # 2 sub lists of 200
        # 1 sub list of the rest: 100
        self.assertEqual(3, len(lists))
        self.assertEqual(200, len(lists[0]))
        self.assertEqual(200, len(lists[1]))
        self.assertEqual(100, len(lists[2]))
