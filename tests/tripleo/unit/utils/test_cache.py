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

from tripleo.utils.cache import Cache, CacheError


class TestCache(TestCase):
    """Tests for :class:`Cache`.
    """

    def test_error_on_none(self):
        """Checks that the cache will not allow 'None' values to be stored
        within it.
        """
        key = 0

        loader = Mock()
        loader.return_value = None

        cache = Cache[int, str](
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

        cache = Cache[int, str](
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

        cache = Cache[int, str](
            loader=loader,
            storage={
                key: value
            }
        )

        self.assertTrue(cache.get(key))
        self.assertEqual(value, cache.get(key))

        loader.assert_not_called()
