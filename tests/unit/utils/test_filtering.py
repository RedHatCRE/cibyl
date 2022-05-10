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

from cibyl.utils.filtering import apply_filters, matches_regex


class TestMatchesRegex(TestCase):
    """Tests for :func:`matches_regex`.
    """

    def test_pattern_is_matches(self):
        """Checks if a text matches a certain regex pattern.
        """
        pattern = '^a...s$'

        self.assertTrue(matches_regex(pattern, 'alias'))
        self.assertTrue(matches_regex(pattern, 'abyss'))
        self.assertFalse(matches_regex(pattern, 'abs'))
        self.assertFalse(matches_regex(pattern, 'word'))

    def test_false_on_invalid_regex(self):
        pattern = '[wod..'

        self.assertFalse(matches_regex(pattern, 'something'))


class TestApplyFilters(TestCase):
    """Tests for :func:`apply_filters`.
    """

    def test_filters_are_applied(self):
        """Checks that the input filters are applied to the data.
        """
        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        filters = [
            lambda number: number >= 5,
            lambda number: number <= 5
        ]

        self.assertEqual([5], apply_filters(data, *filters))
