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
from typing import NamedTuple, Sequence, List, Optional

from xsdata.formats.dataclass.parsers import JsonParser

from cibyl.sources.zuul.apis import Artifact, ArtifactKind
from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.apis.utils.builds import ArtifactError
from cibyl.utils.net import download_into_memory


@dataclass
class ManifestItem:
    name: str = field(
        metadata=dict(type='Element')
    )
    mimetype: str = field(
        metadata=dict(type='Element')
    )
    encoding: Optional[str] = field(
        default=None,
        metadata=dict(type='Element')
    )
    last_modified: Optional[int] = field(
        default=None,
        metadata=dict(type='Element')
    )
    size: Optional[int] = field(
        default=None,
        metadata=dict(type='Element')
    )
    children: Optional[List['ManifestItem']] = field(
        default=None,
        metadata=dict(type='Element')
    )


@dataclass
class Manifest:
    tree: List[ManifestItem] = field(
        default_factory=list,
        metadata=dict(type='Element')
    )
    index_links: bool = field(
        default=False,
        metadata=dict(type='Element')
    )


class ManifestDownloader:
    class DownloadFromBuild:
        def __init__(self, build: Build, tools: 'ManifestDownloader.Tools'):
            self._build = build
            self._tools = tools

        @property
        def build(self):
            return self._build

        @property
        def tools(self):
            return self._tools

        @property
        def session(self):
            return self._build.session.session

        def get_manifest(self) -> Manifest:
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
        parser: JsonParser = JsonParser()

    def __init__(self, tools: Tools = Tools()):
        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def download_from(self, build: Build) -> Manifest:
        downloader = ManifestDownloader.DownloadFromBuild(build, self.tools)

        return downloader.get_manifest()
