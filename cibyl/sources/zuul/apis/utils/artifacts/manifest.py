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
from dataclasses import dataclass, field
from typing import List, NamedTuple, Optional, Sequence

from xsdata.formats.dataclass.parsers import JsonParser

from cibyl.sources.zuul.apis import Artifact, ArtifactKind
from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.apis.utils.artifacts import ArtifactError
from cibyl.utils.net import download_into_memory


@dataclass
class ManifestItem:
    """Schema for one of the elements on the manifest file.
    """
    name: str = field(
        metadata=dict(type='Element')
    )
    """Name of the element."""
    mimetype: str = field(
        metadata=dict(type='Element')
    )
    """Type of the element."""
    encoding: Optional[str] = field(
        default=None,
        metadata=dict(type='Element')
    )
    """Name of the encoding in use, only for files.."""
    last_modified: Optional[int] = field(
        default=None,
        metadata=dict(type='Element')
    )
    """Epoch time when the element was last changed."""
    size: Optional[int] = field(
        default=None,
        metadata=dict(type='Element')
    )
    """Size of the element, only for files."""
    children: Optional[List['ManifestItem']] = field(
        default=None,
        metadata=dict(type='Element')
    )
    """Other elements below this one, only for directories."""


@dataclass
class Manifest:
    """Schema for the manifest file published by a Zuul build.
    """
    tree: List[ManifestItem] = field(
        default_factory=list,
        metadata=dict(type='Element')
    )
    """Tree containing all the logs published by the build."""
    index_links: bool = field(
        default=False,
        metadata=dict(type='Element')
    )


class ManifestDownloader:
    """Utility used to download the manifest published by different sources.
    """

    class DownloadFromBuild:
        """Utility used to retrieve the manifest from a Zuul build.
        """

        def __init__(self, build: Build, tools: 'ManifestDownloader.Tools'):
            """Constructor.

            :param build: Build to get the manifest for.
            :param tools: Tools used by this to perform its task.
            """
            self._build = build
            self._tools = tools

        @property
        def build(self):
            """
            :return: Build to get the manifest for.
            """
            return self._build

        @property
        def tools(self):
            """
            :return: Tools used by this to perform its task.
            """
            return self._tools

        @property
        def session(self):
            """
            :return: Session this uses to perform HTTP tasks.
            """
            return self._build.session.session

        def get_manifest(self) -> Manifest:
            """
            :return: The manifest published by the build.
            """
            manifests = self._retrieve_manifests()

            if len(manifests) == 0:
                raise ArtifactError(
                    f"No manifest file on build: "
                    f"'{self.build.uuid}'."
                )

            if len(manifests) > 1:
                raise ArtifactError(
                    f"More than one manifest file on build: "
                    f"'{self.build.uuid}'."
                )

            return self._download_manifest(manifests[0])

        def _retrieve_manifests(self) -> Sequence[Artifact]:
            return [
                artifact
                for artifact in self.build.artifacts
                if artifact.kind == ArtifactKind.ZUUL_MANIFEST
            ]

        def _download_manifest(self, manifest: Artifact) -> Manifest:
            parser = self.tools.parser

            return parser.from_string(
                download_into_memory(
                    manifest.url, self.session
                ),
                Manifest
            )

    class Tools(NamedTuple):
        """Tools used by this to perform its task.
        """
        parser: JsonParser = JsonParser()
        """Tool used to parse a JSON file into a Python object."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: Tools this uses to perform its task.
        """
        self._tools = tools

    @property
    def tools(self):
        """
        :return: Tools this uses to perform its task.
        """
        return self._tools

    def download_from(self, build: Build) -> Manifest:
        """Gets the manifest published by a particular build.

        :param build: The build to get the manifest for.
        :return: The manifest as a Python object.
        """
        downloader = ManifestDownloader.DownloadFromBuild(build, self.tools)

        return downloader.get_manifest()
