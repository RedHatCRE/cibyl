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
from unittest.mock import Mock

from kernel.tools.cache import CACache, CacheError, RTCache


class TestCACache(TestCase):
    """Tests for :class:`CACache`.
    """

    def test_missing_entry(self):
        """Checks that 'None' is returned for a missing entry.
        """
        key = 0

        cache = CACache[int, str]()

        self.assertFalse(cache.has(key))
        self.assertIsNone(cache.get(key))

    def test_stores_entry(self):
        """Checks that the cache is capable of storing data within.
        """

        key = 0
        value = 'test'

        cache = CACache[int, str]()

        self.assertFalse(cache.has(key))

        cache.put(key, value)

        self.assertTrue(cache.has(key))
        self.assertEqual(value, cache.get(key))

    def test_deletes_entry(self):
        """Checks that it is possible to delete data from the cache.
        """
        key = 0
        value = 'test'

        cache = CACache[int, str](
            storage={
                key: value
            }
        )

        self.assertTrue(cache.has(key))

        cache.delete(key)

        self.assertFalse(cache.has(key))


class TestRTCache(TestCase):
    """Tests for :class:`RTCache`.
    """

    def test_error_on_none(self):
        """Checks that the cache will not allow 'None' values to be stored
        within it.
        """
        key = 0

        loader = Mock()
        loader.return_value = None

        cache = RTCache[int, str](
            loader=loader,
            storage=None
        )

        self.assertFalse(cache.has(key))

        with self.assertRaises(CacheError):
            cache.get(key)

    def test_loads_from_datastore(self):
        """Checks that if the cache is missing a key, it contacts the data's
        origin to retrieve it.
        """
        key = 0
        value = 'some-text'

        loader = Mock()
        loader.return_value = value

        cache = RTCache[int, str](
            loader=loader,
            storage=None
        )

        self.assertFalse(cache.has(key))
        self.assertEqual(value, cache.get(key))
        self.assertTrue(cache.has(key))

        loader.assert_called_once_with(key)

    def test_gets_data_from_cache(self):
        """Checks that if a key is already loaded, then its value is
        obtained from the cache instead of calling the datastore.
        """
        key = 0
        value = 'some-text'

        loader = Mock()

        cache = RTCache[int, str](
            loader=loader,
            storage={
                key: value
            }
        )

        self.assertTrue(cache.get(key))
        self.assertEqual(value, cache.get(key))

        loader.assert_not_called()

    def test_puts_data_from_user(self):
        """Checks that it is possible to modify the cache directly, without
        having to go through the datastore.
        """
        key = 0
        value = 'some-text'

        loader = Mock()

        cache = RTCache[int, str](
            loader=loader,
            storage={}
        )

        cache.put(key, value)

        self.assertTrue(cache.has(key))
        self.assertEqual(value, cache.get(key))

        loader.assert_not_called()

    def test_deletes_entry(self):
        """Checks that it is possible to remove an entry from the cache.
        """
        key = 0
        value = 'some-text'

        loader = Mock()

        cache = RTCache[int, str](
            loader=loader,
            storage={
                key: value
            }
        )

        self.assertTrue(cache.has(key))

        # Check that I can remove the entry
        cache.delete(key)

        self.assertFalse(cache.has(key))

        # Check that nothing happens when I remove again
        cache.delete(key)

        self.assertFalse(cache.has(key))
