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

        variables = {
            variable: value
        }

        variant = Mock()

        search = Mock()
        search.from_variant = Mock()
        search.from_variant.return_value = Mock()
        search.from_variant.return_value.search = Mock()
        search.from_variant.return_value.search.return_value = variables

        tools = Mock()
        tools.variables = search

        finder = VariableSearch(
            search_terms=[variable],
            tools=tools
        )

        self.assertEqual((variable, value), finder.search(variant))

        search.from_variant.assert_called_once_with(variant)

    def test_search_term_priority(self):
        """Checks that the earlier search term on the list will have higher
        priority.
        """
        value1 = '1'
        value2 = '2'

        variable1 = 'term1'
        variable2 = 'term2'

        variables = {
            variable1: value1,
            variable2: value2
        }

        variant = Mock()

        search = Mock()
        search.from_variant = Mock()
        search.from_variant.return_value = Mock()
        search.from_variant.return_value.search = Mock()
        search.from_variant.return_value.search.return_value = variables

        tools = Mock()
        tools.variables = search

        finder = VariableSearch(
            search_terms=[variable1, variable2],
            tools=tools
        )

        self.assertEqual((variable1, value1), finder.search(variant))

        search.from_variant.assert_called_once_with(variant)

    def test_not_found_result(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()

        search = Mock()
        search.from_variant = Mock()
        search.from_variant.return_value = Mock()
        search.from_variant.return_value.search = Mock()
        search.from_variant.return_value.search.return_value = {}

        tools = Mock()
        tools.variables = search

        finder = VariableSearch(
            search_terms=[],
            tools=tools
        )

        self.assertEqual(None, finder.search(variant))

        search.from_variant.assert_called_once_with(variant)


class TestReleaseSearch(TestCase):
    """Tests for :class:`ReleaseSearch`.
    """

    def test_not_found_result(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()

        search = Mock()
        search.from_variant = Mock()
        search.from_variant.return_value = Mock()
        search.from_variant.return_value.search = Mock()
        search.from_variant.return_value.search.return_value = []

        tools = Mock()
        tools.variables = search

        finder = ReleaseSearch(
            search_terms=[],
            tools=tools
        )

        self.assertEqual(None, finder.search(variant))

        search.from_variant.assert_called_once_with(variant)

    def test_transforms_release_into_string(self):
        """Checks that if the release is not provided as a string, this will
        convert it into one before returning it.
        """
        release = 1
        variable = 'release'

        variables = {
            variable: release
        }

        variant = Mock()

        search = Mock()
        search.from_variant = Mock()
        search.from_variant.return_value = Mock()
        search.from_variant.return_value.search = Mock()
        search.from_variant.return_value.search.return_value = variables

        tools = Mock()
        tools.variables = search

        finder = ReleaseSearch(
            search_terms=[variable],
            tools=tools
        )

        self.assertEqual((variable, '1'), finder.search(variant))

        search.from_variant.assert_called_once_with(variant)
