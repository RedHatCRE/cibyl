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
from typing import Iterable

from overrides import overrides


class Comparator(ABC):
    """A comparison function, used to impose a total ordering on some
    collection of objects. Comparators can be passed to sorting algorithms
    to control the order of iterable collections.
    """

    @abstractmethod
    def compare(self, left: object, right: object) -> int:
        """Compares the two arguments for order.

        :param left: First object to be compared.
        :type left: Any
        :param right: Second object to be compared.
        :type right: Any
        :return: A negative integer, zero or a positive integer as the left
            argument is less than, equal to or greater than the right one.
        :rtype: int
        """
        raise NotImplementedError


class NativeComparator(Comparator):
    """Implements a comparison function using Python's native resources.
    This is, comparison of two objects will be performed through their
    '__eq__' and '__lt__' methods."""

    @overrides
    def compare(self, left: object, right: object) -> int:
        if left == right:
            return 0

        return -1 if left < right else 1


class SortingAlgorithm(ABC):
    """Base class for a sorting algorithms. These algorithms are used to
    reorder the elements of a collection following a set of certain rules.
    These rules are defines by the comparator in use.
    """

    def __init__(self, comparator: 'Comparator' = NativeComparator()) -> None:
        """Constructor.

        :param comparator: Comparison function this uses to determine order.
        :type comparator: :class:`Comparator`
        """
        self._comparator = comparator

    @abstractmethod
    def sort(self, iterable: Iterable) -> None:
        """Sorts the given collection in ascending order. The original
        collection remains untouched, instead, a sorted copy of it is returned.

        :param iterable: The collection to be sorted.
        :type iterable: :class:`typing.Iterable`
        :return: The same collection, sorted following this algorithm's
            comparator.
        :rtype: list
        """
        raise NotImplementedError


class BubbleSortAlgorithm(SortingAlgorithm):
    """Implementation of the Bubble-Sort algorithm. See more at:
    https://en.wikipedia.org/wiki/Bubble_sort
    """

    @overrides
    def sort(self, iterable: Iterable) -> None:
        def compare(lft, rght):
            return self._comparator.compare(lft, rght)

        result = list(iterable)  # Do not affect the original list

        for i in range(len(result)):
            for j in range(0, len(result) - i - 1):
                if compare(result[j], result[j + 1]) > 0:
                    temp = result[j]

                    # Swap the two cells
                    result[j] = result[j + 1]
                    result[j + 1] = temp

        return result


def sort(iterable, algorithm: Iterable = BubbleSortAlgorithm()) -> list:
    """Shortcut for sorting the elements of a collection.

    :param iterable: The collection to sort.
    :type iterable: :class:`typing.Iterable`
    :param algorithm: The algorithm that will be used to sort the collection.
        Contains the comparator used to determine order.
    :type algorithm: :class:`SortingAlgorithm`
    :return: A copy of the input collection, sorted by the algorithm.
    :rtype: list
    """
    return algorithm.sort(iterable)


def nsort(iterable, algorithm: Iterable = BubbleSortAlgorithm()) -> Iterable:
    """Same as :func:`sort`, but this one reverses the collection before
    returning it. Use this function to get sorting in descending order.
    """
    result = sort(iterable, algorithm)
    result.reverse()
    return result
