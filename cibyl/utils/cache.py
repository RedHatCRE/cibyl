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
from typing import Generic, MutableMapping, Optional, TypeVar

K = TypeVar('K')
"""Type of keys used by the cache."""
V = TypeVar('V')
"""Type of data used by the cache."""


class Cache(Generic[K, V]):
    """A cache is a map-like data structure that provides temporary storage
    of application data.

    Like maps, it:
        - Stores key -> value pairs.
        - Allows use of generics to define data types.
    Unlike maps, it:
        - Does not allow 'None' values to be stored.

    This implementation follows the Cache-Aside approach to caching.
    This means that the cache is a simple container for others to push to and
    pull from. It does not have any responsibility regarding the origin of
    data and how it is retrieved. Those are up to the user to assume.
    """

    def __init__(
        self,
        storage: Optional[MutableMapping[K, V]] = None
    ):
        """Constructor.

        :param storage: Container where the cached data is stored. Be sure
            that the structure follows the specifications of this class.
            'None' to let this create its own.
        """
        if storage is None:
            storage = {}

        self._storage = storage

    @property
    def storage(self):
        """
        :return: Container where the cached data is stored. Modifications to
            this structure can lead to a corrupted cache, use under your own
            responsibility.
        """
        return self._storage

    def has(self, key: K) -> bool:
        """Checks if the cache contains a value for the given key.

        :param key: The key to test.
        :return: True if it does, False if not.
        """
        return key in self.storage

    def get(self, key: K) -> Optional[V]:
        """Gets the value for an entry in the cache.

        :param key: The key to get the value for.
        :return: The value associated to the key if is it present on the
        cache, 'None' if not.
        """
        return self.storage.get(key)

    def put(self, key: K, value: V) -> None:
        """Creates a new entry on the cache. If the entry already exists,
        then it will be overridden.

        :param key: Key for the entry.
        :param value: Data associated to the key.
        :return:
        """
        self.storage[key] = value
