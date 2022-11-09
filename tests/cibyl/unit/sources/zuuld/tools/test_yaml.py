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
from unittest.mock import Mock, call

from cibyl.sources.zuuld.tools.yaml import YAMLSearch


class TestYAMLSearch(TestCase):
    """Tests for :class;`YAMLSearch`.
    """

    def test_root_is_passed(self):
        """Checks that the given root directory is the one used for the
        search.
        """
        root = Mock()

        builder = Mock()
        builder.with_recursion = Mock()
        builder.with_extension = Mock()
        builder.get = Mock()
        builder.get.return_value = []

        factory = Mock()
        factory.from_root = Mock()
        factory.from_root.return_value = builder

        tools = Mock()
        tools.files = factory

        search = YAMLSearch(
            tools=tools
        )

        search.search(path=root)

        factory.from_root.assert_called_once_with(root)

    def test_search_is_recursive(self):
        """Checks that the search is requested to be recursive.
        """
        root = Mock()

        builder = Mock()
        builder.with_recursion = Mock()
        builder.with_extension = Mock()
        builder.get = Mock()
        builder.get.return_value = []

        factory = Mock()
        factory.from_root = Mock()
        factory.from_root.return_value = builder

        tools = Mock()
        tools.files = factory

        search = YAMLSearch(
            tools=tools
        )

        search.search(path=root)

        builder.with_recursion.assert_called()

    def test_search_filters_by_extensions(self):
        """Checks that the search filters by the extensions known by the class.
        """
        root = Mock()
        extensions = [Mock(), Mock()]

        builder = Mock()
        builder.with_recursion = Mock()
        builder.with_extension = Mock()
        builder.get = Mock()
        builder.get.return_value = []

        factory = Mock()
        factory.from_root = Mock()
        factory.from_root.return_value = builder

        tools = Mock()
        tools.files = factory

        search = YAMLSearch(
            extensions=extensions,
            tools=tools
        )

        search.search(path=root)

        builder.with_extension.assert_has_calls(
            calls=[
                call(extensions[0]),
                call(extensions[1])
            ]
        )

    def test_returns_files(self):
        """Checks that the found files are returned.
        """
        root = Mock()
        expected = ['path-1', 'path-2']

        builder = Mock()
        builder.with_recursion = Mock()
        builder.with_extension = Mock()
        builder.get = Mock()
        builder.get.return_value = expected

        factory = Mock()
        factory.from_root = Mock()
        factory.from_root.return_value = builder

        tools = Mock()
        tools.files = factory

        search = YAMLSearch(
            tools=tools
        )

        result = search.search(path=root)

        self.assertEqual(expected, result)
