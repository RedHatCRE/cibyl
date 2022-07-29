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
from cibyl.sources.zuul.apis.utils.artifacts.manifest import \
    ManifestDownloader, Manifest
from cibyl.sources.zuul.apis.utils.builds import ArtifactError


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

        module = cibyl.sources.zuul.apis.utils.artifacts.manifest
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
