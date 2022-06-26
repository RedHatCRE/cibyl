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

from cibyl.utils.sorting import (BubbleSortAlgorithm, NativeComparator, nsort,
                                 sort)


class TestNativeComparator(TestCase):
    """Tests for :class:`NativeComparator`.
    """

    class TestClass:
        def __init__(self, value):
            self._value = value

        @property
        def value(self):
            return self._value

        def __eq__(self, other):
            return self.value == other.value

        def __lt__(self, other):
            return self.value <= other.value

    def test_are_equal(self):
        """Checks that two objects are equal if their __eq__ said so.
        """
        object1 = TestNativeComparator.TestClass(1)
        object2 = TestNativeComparator.TestClass(1)

        comparator = NativeComparator()

        self.assertEqual(0, comparator.compare(object1, object2))

    def test_is_less_than(self):
        """Checks that an object is less that another if their __lt__ said
        so.
        """
        object1 = TestNativeComparator.TestClass(0)
        object2 = TestNativeComparator.TestClass(1)

        comparator = NativeComparator()

        self.assertEqual(-1, comparator.compare(object1, object2))

    def test_is_greater_than(self):
        """Checks that an object is greater that another if their __lt__ said
        so.
        """
        object1 = TestNativeComparator.TestClass(2)
        object2 = TestNativeComparator.TestClass(1)

        comparator = NativeComparator()

        self.assertEqual(1, comparator.compare(object1, object2))


class TestBubbleSortAlgorithm(TestCase):
    """Tests for :class:`BubbleSortAlgorithm`.
    """

    def test_sorts_from_lesser_to_greater(self):
        """Checks that the sorter sorts properly going from the lowest
        value to the highest.
        """
        unsorted = [13, 3, -8, 7, -2]

        sorter = BubbleSortAlgorithm()

        self.assertEqual(
            [-8, -2, 3, 7, 13],
            sorter.sort(unsorted)
        )


class TestSort(TestCase):
    """Tests for :func:`sort`.
    """

    def test_sorts_from_lesser_to_greater(self):
        """Checks that the function sorts properly going from the lowest
        value to the highest.
        """
        unsorted = [13, 3, -8, 7, -2]

        self.assertEqual(
            [-8, -2, 3, 7, 13],
            sort(unsorted)
        )


class TestNSort(TestCase):
    """Tests for :func:`nsort`.
    """

    def test_sorts_from_greater_to_lessed(self):
        """Checks that the function sorts properly going from the highest
        value to the lowest.
        """
        unsorted = [13, 3, -8, 7, -2]

        self.assertEqual(
            [13, 7, 3, -2, -8],
            nsort(unsorted)
        )
