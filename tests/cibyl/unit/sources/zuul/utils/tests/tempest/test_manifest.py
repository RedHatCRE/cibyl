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

from cibyl.sources.zuul.utils.artifacts import ArtifactError
from cibyl.sources.zuul.utils.tests.tempest.manifest import (
    ManifestDigger, TempestResultsFinder)


class TestManifestDigger(TestCase):
    """Tests for :class:`ManifestDigger`.
    """

    def test_error_on_invalid_level(self):
        """Checks that an error is thrown in case the user tries to delve
        into a level that does not exist.
        """
        level = 'some-level'

        manifest = Mock()
        manifest.tree = []

        digger = ManifestDigger(manifest)

        self.assertFalse(digger.has_sublevel(level))

        with self.assertRaises(ArtifactError):
            digger.delve_into(level)

    def test_delves_into_level(self):
        """Checks that it is capable to switch the current level if it does
        exist.
        """
        level = 'some-level'

        other = Mock()

        item = Mock()
        item.name = level
        item.children = [other]

        manifest = Mock()
        manifest.tree = [item]

        digger = ManifestDigger(manifest)

        self.assertTrue(digger.has_sublevel(level))

        digger.delve_into(level)

        self.assertEqual([other], digger.current_level)


class TestResultsFinder(TestCase):
    """Tests for :class:`TempestResultsFinder`.
    """

    def test_finds_results_on_manifest(self):
        """Checks that it is capable of finding the results file in a
        manifest that has it somewhere on its tree.
        """
        item = Mock()
        item.name = 'item'

        manifest = Mock()
        manifest.tree = [item]

        digger = Mock()
        digger.delve_into = Mock()
        digger.has_sublevel = Mock()
        digger.has_sublevel.return_value = True
        digger.current_level = manifest.tree

        search_terms = Mock()
        search_terms.paths = ('',)
        search_terms.files = (item.name,)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = TempestResultsFinder(search_terms=search_terms, tools=tools)

        result = finder.find_in(manifest)

        self.assertIsNotNone(result)
        self.assertEqual(item.name, result)

    def test_no_results_if_not_on_path(self):
        """Checks returned value if the requested file is not at the
        indicated level.
        """
        item = Mock()
        item.name = 'item'

        manifest = Mock()
        manifest.tree = [item]

        digger = Mock()
        digger.delve_into = Mock()
        digger.has_sublevel = Mock()
        digger.has_sublevel.return_value = True
        digger.current_level = manifest.tree

        search_terms = Mock()
        search_terms.paths = ('',)
        search_terms.files = ('file',)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = TempestResultsFinder(search_terms=search_terms, tools=tools)

        result = finder.find_in(manifest)

        self.assertIsNone(result)

    def test_no_results_if_no_path(self):
        """Checks returned value if the indicated path does not exist on the
        manifest.
        """
        manifest = Mock()
        manifest.tree = []

        digger = Mock()
        digger.delve_into = Mock()
        digger.has_sublevel = Mock()
        digger.has_sublevel.return_value = True
        digger.current_level = manifest.tree

        search_terms = Mock()
        search_terms.paths = ('some_path',)
        search_terms.files = ('file',)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = TempestResultsFinder(search_terms=search_terms, tools=tools)

        result = finder.find_in(manifest)

        self.assertIsNone(result)
