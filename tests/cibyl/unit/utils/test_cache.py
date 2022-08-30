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

from cibyl.utils.cache import Cache


class TestCache(TestCase):
    """Tests for :class:`Cache`.
    """

    def test_none_if_unknown(self):
        """Checks that 'None' is returned if a key is not on the cache.
        """
        key = 1

        cache = Cache[int, str]()

        self.assertFalse(cache.has(key))
        self.assertIsNone(cache.get(key))

    def test_adds_key(self):
        """Checks that the cache is able to create a new entry within.
        """
        key = 1
        value = 'some_text'

        cache = Cache[int, str]()

        self.assertFalse(cache.has(key))

        cache.put(key, value)

        self.assertTrue(cache.has(key))
        self.assertEqual(value, cache.get(key))

    def test_overrides_data(self):
        """Checks that if I add something new to a known key, the data for
        that key will be overridden.
        """
        key = 1

        val1 = 'text1'
        val2 = 'text2'

        cache = Cache[int, str](
            storage={
                key: val1
            }
        )

        self.assertEqual(val1, cache.get(key))

        cache.put(key, val2)

        self.assertEqual(val2, cache.get(key))
