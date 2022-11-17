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
from abc import ABC, abstractmethod
from typing import Callable, Generic, MutableMapping, Optional, TypeVar

from overrides import overrides

K = TypeVar('K')
"""Type of keys used by the cache."""
V = TypeVar('V')
"""Type of data used by the cache."""


class CacheError(Exception):
    """Indicates that an error has occurred in the cache.
    """


class Cache(Generic[K, V], ABC):
    """A cache is a map-like data structure that provides temporary storage
    of application data.

    Like maps, it:
        - Stores key -> value pairs.
        - Allows use of generics to define data types.
    Unlike maps, it:
        - Does not allow 'None' values to be stored.
    """

    @abstractmethod
    def has(self, key: K) -> bool:
        """Checks if there is an entry on the cache with a value for the
        given key.

        :param key: The key to test.
        :return: True if it does, False if not.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: K) -> V:
        """Gets the value for an entry in the cache.

        :param key: Key to the entry to get the value from.
        :return: Value stored at the entry.
        :raises CacheError:
            If the entry does not exist on the cache.
            If the value could not be retrieved from the entry.
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, key: K, value: V) -> None:
        """Creates an entry in the cache indexed through the given key.
        If the entry already exists, then it is overwritten with the new
        value. It is recommended to always check for the entry beforehand.

        :param key: Key to reference the value by.
        :param value: Data to store.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: K) -> None:
        """Deletes an entry in the cache. Does nothing if the entry already
        does not exist.

        :param key: Key to the entry to remove.
        """
        raise NotImplementedError


class CACache(Cache[K, V]):
    """This implementation follows the Cache-Aside approach to caching.
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

    @overrides
    def has(self, key: K) -> bool:
        return key in self.storage

    @overrides
    def get(self, key: K) -> Optional[V]:
        return self.storage.get(key)

    @overrides
    def put(self, key: K, value: V) -> None:
        self.storage[key] = value

    @overrides
    def delete(self, key: K) -> None:
        if key not in self.storage:
            return

        del self.storage[key]


class RTCache(Cache[K, V]):
    """Implementation that follows the Read-Through approach to caching.
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
            datastore. Will be called whenever the cache cannot retrieve
            the value for a certain key.
        :param storage: Container where cached data is stored. Be sure
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
        :return: Container where cached data is stored. Modifications to
            this structure can lead to a corrupted cache, use under your own
            responsibility.
        """
        return self._storage

    @overrides
    def has(self, key: K) -> bool:
        return key in self.storage

    @overrides
    def get(self, key: K) -> V:
        """Gets the value for an entry in the cache. If the cache is
        missing so, then the datastore is reached in order to load one.

        :param key: Key to the entry to get the value from.
        :return: Value stored at the entry.
        :raises CacheError:
            If the datastore answered with a 'None' value.
        """
        if not self.has(key):
            self._load(key)

        return self.storage[key]

    def _load(self, key: K) -> None:
        """Retrieves a value from the datastore and stores it at the entry
        indexed by the given key. If the entry already exists, then its
        contents get overwritten by what the datastore returned.

        :param key: Key to the entry to get the value for.
        :raises CacheError:
            If the datastore answered the request with a 'None' value.
        """
        value = self.loader(key)

        if value is None:
            raise CacheError(
                f"Datastore responded with a 'None' value to key: '{key}'."
            )

        self.put(key, value)

    @overrides
    def put(self, key: K, value: V) -> None:
        self.storage[key] = value

    @overrides
    def delete(self, key: K) -> None:
        if key not in self.storage:
            return

        del self.storage[key]
