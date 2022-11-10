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
from unittest.mock import MagicMock, Mock, call

from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.tools.yaml import YAMLReader, YAMLSearch


class TestYAMLReader(TestCase):
    """Tests for :class:`YAMLReader`.
    """

    def test_parses_jobs(self):
        """Checks that the reader is capable of forming job models from the
        data in the file.
        """
        data = [
            {
                'job': {
                    'name': 'job1',
                    'branches': 'master'
                }
            },
            {
                'job': {
                    'name': 'job2',
                    'parent': 'job1',
                    'branches': [
                        'main',
                        'devel'
                    ],
                    'vars': {
                        'test': 'var'
                    }
                }
            }
        ]

        file = Mock()
        file.data = data

        reader = YAMLReader(file)

        result = list(reader.jobs())

        self.assertEqual(
            Job(
                name='job1',
                branches=['master']
            ),
            result[0]
        )

        self.assertEqual(
            Job(
                name='job2',
                parent='job1',
                branches=['main', 'devel'],
                vars={'test': 'var'}
            ),
            result[1]
        )


class TestYAMLSearch(TestCase):
    """Tests for :class:`YAMLSearch`.
    """

    def test_root_is_passed(self):
        """Checks that the given root directory is the one used for the
        search.
        """
        root = Mock()

        search = Mock()
        search.get = MagicMock()

        searches = Mock()
        searches.from_root = Mock()
        searches.from_root.return_value = search

        tools = Mock()
        tools.searches = searches

        yaml = YAMLSearch(
            tools=tools
        )

        yaml.search(path=root)

        searches.from_root.assert_called_with(root)

    def test_search_is_recursive(self):
        """Checks that the search is requested to be recursive.
        """
        root = Mock()

        search = Mock()
        search.with_recursion = Mock()
        search.get = MagicMock()

        searches = Mock()
        searches.from_root = Mock()
        searches.from_root.return_value = search

        tools = Mock()
        tools.searches = searches

        yaml = YAMLSearch(
            tools=tools
        )

        yaml.search(path=root)

        search.with_recursion.assert_called()

    def test_search_filters_by_extensions(self):
        """Checks that the search filters by the extensions known by the class.
        """
        root = Mock()
        extensions = [Mock(), Mock()]

        search = Mock()
        search.with_extension = Mock()
        search.get = MagicMock()

        searches = Mock()
        searches.from_root = Mock()
        searches.from_root.return_value = search

        tools = Mock()
        tools.searches = searches

        yaml = YAMLSearch(
            extensions=extensions,
            tools=tools
        )

        yaml.search(path=root)

        search.with_extension.assert_has_calls(
            calls=[
                call(extensions[0]),
                call(extensions[1])
            ]
        )

    def test_returns_files(self):
        """Checks that the found files are returned.
        """
        root = Mock()

        # Reusing this mock for before and after becoming a YAMLFile.
        file1 = 'file1.yml'
        file2 = 'file2.yml'

        files = Mock()
        files.from_file = Mock()
        files.from_file.side_effect = lambda file, **_: file

        search = Mock()
        search.get = Mock()
        search.get.return_value = [file1, file2]

        searches = Mock()
        searches.from_root = Mock()
        searches.from_root.return_value = search

        tools = Mock()
        tools.searches = searches
        tools.files = files

        yaml = YAMLSearch(
            tools=tools
        )

        result = yaml.search(path=root)

        self.assertEqual([file1, file2], result)
