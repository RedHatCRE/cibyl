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

import cibyl
from cibyl.sources.zuul.apis import ArtifactKind
from cibyl.sources.zuul.utils.artifacts import ArtifactError
from cibyl.sources.zuul.utils.artifacts.manifest import (Manifest,
                                                         ManifestDigger,
                                                         ManifestDir,
                                                         ManifestDownloader,
                                                         ManifestFile,
                                                         ManifestFileSearch)


class TestManifestDownloader(TestCase):
    """Tests for :class:`ManifestDownloader`.
    """

    def test_no_manifests_on_build(self):
        """Checks that an error is thrown if there are no manifest files on
        the build.
        """
        tools = Mock()
        tools.parser = Mock()

        build = Mock()
        build.artifacts = []

        downloader = ManifestDownloader(tools=tools)

        with self.assertRaises(ArtifactError):
            downloader.download_from(build)

    def test_too_many_manifests_on_build(self):
        """Checks that an error is thrown if more than one manifest file
        are on the build.
        """
        artifact1 = Mock()
        artifact1.kind = ArtifactKind.ZUUL_MANIFEST

        artifact2 = Mock()
        artifact2.kind = ArtifactKind.ZUUL_MANIFEST

        tools = Mock()
        tools.parser = Mock()

        build = Mock()
        build.artifacts = [artifact1, artifact2]

        downloader = ManifestDownloader(tools=tools)

        with self.assertRaises(ArtifactError):
            downloader.download_from(build)

    def test_gets_manifest(self):
        """Checks that if an artifact is present for it, the manifest is
        returned.
        """
        url = 'some-url'
        json = 'some-json'

        session = Mock()
        manifest = Mock()

        artifact = Mock()
        artifact.kind = ArtifactKind.ZUUL_MANIFEST
        artifact.url = url

        build = Mock()
        build.artifacts = [artifact]
        build.session.session = session

        module = cibyl.sources.zuul.utils.artifacts.manifest
        download = module.download_into_memory = Mock()
        download.return_value = json

        tools = Mock()
        tools.parser = Mock()
        tools.parser.from_string = Mock()
        tools.parser.from_string.return_value = manifest

        downloader = ManifestDownloader(tools=tools)

        result = downloader.download_from(build)

        self.assertEqual(manifest, result)

        download.assert_called_once_with(url, session)
        tools.parser.from_string.assert_called_once_with(json, Manifest)


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


class TestManifestDir(TestCase):
    """Tests for :class:`ManifestDir`.
    """

    def test_regex_pattern(self):
        """Checks that the regex pattern matches what the description says.
        """
        try:
            ManifestDir('/')
        except ValueError:
            self.fail('Pattern is valid.')

        try:
            ManifestDir('/var/logs/tempest')
        except ValueError:
            self.fail('Pattern is valid.')

        with self.assertRaises(ValueError):
            ManifestDir('home/logs')

        with self.assertRaises(ValueError):
            ManifestDir('/home/zuul/')


class TestManifestFile(TestCase):
    """Tests for :class:`ManifestFile`.
    """

    def test_regex_pattern(self):
        """Checks that the regex pattern matches what the description says.
        """
        try:
            ManifestFile('/file.txt')
        except ValueError:
            self.fail('Pattern is valid.')

        try:
            ManifestFile('/var/logs/tempest/results.xml')
        except ValueError:
            self.fail('Pattern is valid.')

        with self.assertRaises(ValueError):
            ManifestFile('home/file.txt')

        with self.assertRaises(ValueError):
            ManifestFile('/var/logs/file')


class TestManifestFileSearch(TestCase):
    """Tests for :class:`ManifestFileSearch`.
    """

    def test_finds_results_on_manifest(self):
        """Checks that it is capable of finding the results file in a
        manifest that has it somewhere on its tree.
        """
        path = '/'

        item = Mock()
        item.name = 'item.txt'

        manifest = Mock()
        manifest.tree = [item]

        digger = Mock()
        digger.delve_into = Mock()
        digger.has_sublevel = Mock()
        digger.has_sublevel.return_value = True
        digger.current_level = manifest.tree

        search_terms = Mock()
        search_terms.paths = (path,)
        search_terms.files = (item.name,)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = ManifestFileSearch(tools=tools)

        result = finder.find_in(manifest, search_terms)

        self.assertIsNotNone(result)
        self.assertEqual((f'{path}{item.name}', item), result)

    def test_no_results_if_not_on_path(self):
        """Checks returned value if the requested file is not at the
        indicated level.
        """
        item = Mock()
        item.name = 'item.txt'

        manifest = Mock()
        manifest.tree = [item]

        digger = Mock()
        digger.delve_into = Mock()
        digger.has_sublevel = Mock()
        digger.has_sublevel.return_value = True
        digger.current_level = manifest.tree

        search_terms = Mock()
        search_terms.paths = ('/',)
        search_terms.files = ('other.txt',)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = ManifestFileSearch(tools=tools)

        result = finder.find_in(manifest, search_terms)

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
        search_terms.paths = ('/some/path',)
        search_terms.files = ('other.txt',)

        tools = Mock()
        tools.diggers = Mock()
        tools.diggers.from_manifest = Mock()
        tools.diggers.from_manifest.return_value = digger

        finder = ManifestFileSearch(tools=tools)

        result = finder.find_in(manifest, search_terms)

        self.assertIsNone(result)
