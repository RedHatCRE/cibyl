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
from typing import Callable, Generic, MutableMapping, Optional, TypeVar

K = TypeVar('K')
"""Type of keys used by the cache."""
V = TypeVar('V')
"""Type of data used by the cache."""


class CacheError(Exception):
    """Indicates that an error has occurred in the cache.
    """


class Cache(Generic[K, V]):
    """A cache is a map-like data structure that provides temporary storage
    of application data.

    Like maps, it:
        - Stores key -> value pairs.
        - Allows use of generics to define data types.
    Unlike maps, it:
        - Does not allow 'None' values to be stored.

    This implementation follows the Read-Through approach to caching.
    This means that the cache takes responsibility of reaching the
    datastore for values it has not within yet.
    """

    def __init__(
        self,
        loader: Callable[[K], V],
        storage: Optional[MutableMapping[K, V]] = None
    ):
        """Constructor.

        :param loader: Function that allows the cache to get data from the
            datastore.
        :param storage: Container where the cached data is stored. Be sure
            that the structure follows the specifications of this class.
            'None' to let this create its own.
        """
        if storage is None:
            storage = {}

        self._loader = loader
        self._storage = storage

    @property
    def loader(self) -> Callable[[K], V]:
        """
        :return: Function that allows the cache to get data from the datastore.
        """
        return self._loader

    @property
    def storage(self) -> MutableMapping[K, V]:
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

    def get(self, key: K) -> V:
        """Gets the value for a key in the cache. If the cache is missing a
        value for the key, then the datastore is reached in order to
        load one.

        :param key: The key to get the value for.
        :return: Value for the key.
        :raises CacheError: If the datastore answered the cache with a
            'None' value.
        """
        if not self.has(key):
            self._load(key)

        return self.storage[key]

    def _load(self, key: K) -> None:
        """Retrieves a value from the datastore and stores it in this.

        :param key: Key to get the value for.
        :raises CacheError: If the datastore answered the request with a
            'None' value.
        """
        value = self.loader(key)

        if value is None:
            raise CacheError(
                f"Datastore responded with a 'None' value to key: '{key}'."
            )

        self._put(key, value)

    def _put(self, key: K, value: V) -> None:
        """Creates an entry on the cache. If the entry already exists,
        then it is overwritten with these new values.

        :param key: Key to store the value.
        :param value: Data to store.
        """
        self.storage[key] = value
