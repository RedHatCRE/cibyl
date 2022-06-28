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

from cibyl.plugins.openstack.sources.zuul.variants import (ReleaseSearch,
                                                           VariableSearch)


class TestVariableSearch(TestCase):
    """Tests for :class:`VariableSearch`.
    """

    def test_finds_variable_in_variant(self):
        """Checks that the search is capable of finding the desires variable.
        """
        value = 'val1'
        variable = 'var1'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            variable: value
        }

        finder = VariableSearch([variable])

        self.assertEqual(value, finder.search(variant))

        variant.variables.assert_called_once_with(recursive=True)

    def test_search_term_priority(self):
        """Checks that the earlier search term on the list will have higher
        priority.
        """
        value1 = '1'
        value2 = '2'

        variable1 = 'term1'
        variable2 = 'term2'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            variable1: value1,
            variable2: value2,
        }

        finder = VariableSearch(search_terms=[variable1, variable2])

        self.assertEqual(value1, finder.search(variant))

    def test_not_found_result(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
        }

        finder = VariableSearch(search_terms=[])

        self.assertEqual(None, finder.search(variant))


class TestReleaseSearch(TestCase):
    """Tests for :class:`ReleaseSearch`.
    """

    def test_not_found_result(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
        }

        finder = ReleaseSearch(search_terms=[])

        self.assertEqual(None, finder.search(variant))

    def test_transforms_release_into_string(self):
        """Checks that if the release is not provided as a string, this will
        convert it into one before returning it.
        """
        release = 1
        variable = 'release'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            variable: release
        }

        search = ReleaseSearch(search_terms=[variable])

        self.assertEqual('1', search.search(variant))
