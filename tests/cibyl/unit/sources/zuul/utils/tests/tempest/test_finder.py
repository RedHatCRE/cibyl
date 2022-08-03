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

from cibyl.sources.zuul.utils.tests.tempest.finder import TempestTestFinder


class TestTempestTestFinder(TestCase):
    """Tests for :class:`TempestTestFinder`.
    """

    def test_no_results(self):
        """Checks that an empty collection is returned if the results xml
        could not be found.
        """
        build = Mock()

        config = Mock()
        config.search_terms = Mock()

        manifest = Mock()

        downloader = Mock()
        downloader.download_from = Mock()
        downloader.download_from.return_value = manifest

        search = Mock()
        search.find_in = Mock()
        search.find_in.return_value = None

        tools = Mock()
        tools.manifest = downloader
        tools.search = search

        finder = TempestTestFinder(config=config, tools=tools)

        result = finder.find(build)

        self.assertEqual(0, len(list(result)))

        downloader.download_from.assert_called_once_with(build)
        search.find_in.assert_called_once_with(manifest, config.search_terms)

    def test_gets_tests(self):
        """Checks that if the tempest results xml is retrieved, then the
        tests inside are parsed and returned.
        """
        tests = Mock()

        build = Mock()

        config = Mock()
        config.search_terms = Mock()

        file = Mock()
        manifest = Mock()

        downloader = Mock()
        downloader.download_from = Mock()
        downloader.download_from.return_value = manifest

        search = Mock()
        search.find_in = Mock()
        search.find_in.return_value = (file, None)

        parser = Mock()
        parser.parse_tests_at = Mock()
        parser.parse_tests_at.return_value = tests

        tools = Mock()
        tools.manifest = downloader
        tools.search = search
        tools.parser = parser

        finder = TempestTestFinder(config=config, tools=tools)

        result = finder.find(build)

        self.assertEqual(tests, result)

        downloader.download_from.assert_called_once_with(build)
        search.find_in.assert_called_once_with(manifest, config.search_terms)
        parser.parse_tests_at.assert_called_once_with(build, file)
