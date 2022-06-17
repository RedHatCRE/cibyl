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

from overrides import overrides


class Comparator(ABC):
    @abstractmethod
    def compare(self, left, right):
        raise NotImplementedError


class NativeComparator(Comparator):
    @overrides
    def compare(self, left, right):
        if left == right:
            return 0

        return -1 if left < right else 1


class SortingAlgorithm(ABC):
    def __init__(self, comparator=NativeComparator()):
        self._comparator = comparator

    @abstractmethod
    def sort(self, iterable):
        raise NotImplementedError


class BubbleSortAlgorithm(SortingAlgorithm):
    @overrides
    def sort(self, iterable):
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


def sort(iterable, algorithm=BubbleSortAlgorithm()):
    return algorithm.sort(iterable)


def nsort(iterable, algorithm=BubbleSortAlgorithm()):
    result = sort(iterable, algorithm)
    result.reverse()
    return result
