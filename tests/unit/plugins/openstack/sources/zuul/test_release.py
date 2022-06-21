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

from cibyl.plugins.openstack.sources.zuul.release import ReleaseFinder


class TestReleaseFinder(TestCase):
    """Tests for :class:`ReleaseFinder`.
    """

    def test_finds_release_in_variant(self):
        """Checks that the release is found if one of the search terms
        appear on the variant's variables.
        """
        release = '1'
        search_term = 'release'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            search_term: release
        }

        finder = ReleaseFinder(search_terms=[search_term])

        self.assertEqual(
            release,
            finder.find_release_for(variant)
        )

        variant.variables.assert_called_once()

    def test_finds_release_in_parent(self):
        """Checks that the finder requests the variables of the variant's
        parents as well.
        """
        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
        }

        finder = ReleaseFinder()

        finder.find_release_for(variant)

        variant.variables.assert_called_once_with(recursive=True)

    def test_search_term_priority(self):
        """Checks that the earlier search term on the list will have higher
        priority.
        """
        release1 = '1'
        release2 = '2'

        search_term1 = 'term1'
        search_term2 = 'term2'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            search_term1: release1,
            search_term2: release2,
        }

        finder = ReleaseFinder(search_terms=[search_term1, search_term2])

        self.assertEqual(
            release1,
            finder.find_release_for(variant)
        )

    def test_not_found_result(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
        }

        finder = ReleaseFinder(search_terms=[])

        self.assertEqual(
            None,
            finder.find_release_for(variant)
        )

    def test_transforms_release_into_string(self):
        """Checks that if the release is not provided as a string, this will
        convert it into one before returning it.
        """
        release = 1
        search_term = 'release'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            search_term: release
        }

        finder = ReleaseFinder(search_terms=[search_term])

        self.assertEqual(
            '1',
            finder.find_release_for(variant)
        )
