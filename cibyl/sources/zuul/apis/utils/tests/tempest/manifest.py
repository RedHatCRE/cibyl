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
from typing import Iterable, NamedTuple, Optional

from cibyl.sources.zuul.apis.utils.artifacts import ArtifactError
from cibyl.sources.zuul.apis.utils.artifacts.manifest import (Manifest,
                                                              ManifestItem)

ManifestLevel = Iterable[ManifestItem]


class ManifestDigger:
    def __init__(self, manifest: Manifest):
        self._manifest = manifest
        self._current_level = manifest.tree

    @property
    def manifest(self) -> Manifest:
        return self._manifest

    @property
    def current_level(self) -> ManifestLevel:
        return self._current_level

    def has_sublevel(self, name: str) -> bool:
        return bool(self._get_sublevel(name))

    def delve_into(self, level: str) -> None:
        if not self.has_sublevel(level):
            msg = f"Manifest has no level: '{level}'."
            raise ArtifactError(msg)

        self._current_level = self._get_sublevel(level)

    def _get_sublevel(self, level: str) -> Optional[ManifestLevel]:
        for item in self.current_level:
            if item.name != level:
                continue

            if not item.children:
                return None

            return item.children

        return None


class ManifestDiggerFactory:
    def from_manifest(self, manifest: Manifest) -> ManifestDigger:
        return ManifestDigger(manifest)


class TempestResultsFinder:
    class SearchTerms(NamedTuple):
        DEFAULT_RESULTS_PATHS = (
            'logs/undercloud/var/log/tempest',
        )

        DEFAULT_RESULTS_FILES = (
            'tempest_results.xml',
            'tempest_results.xml.gz'
        )

        paths: Iterable[str] = DEFAULT_RESULTS_PATHS
        files: Iterable[str] = DEFAULT_RESULTS_FILES

    class Tools(NamedTuple):
        diggers: ManifestDiggerFactory = ManifestDiggerFactory()

    def __init__(
        self,
        search_terms: SearchTerms = SearchTerms(),
        tools: Tools = Tools()
    ):
        self._search_terms = search_terms
        self._tools = tools

    @property
    def search_terms(self):
        return self._search_terms

    @property
    def tools(self):
        return self._tools

    def find_in(self, manifest: Manifest) -> Optional[str]:
        for path in self.search_terms.paths:
            path = self._preprocess_path(path)
            level = self._get_manifest_level(manifest, path)

            if not level:
                # The file's directory does not exist
                continue

            for file in self.search_terms.files:
                # See if the file is at this level
                results = next(
                    (item for item in level if item.name == file),
                    None
                )

                if not results:
                    # The file is not here
                    continue

                if not path:
                    # In case it is on the manifest's root
                    return file

                # Generate path to the file
                return f'{path}/{file}'

        return None

    def _get_manifest_level(
        self,
        manifest: Manifest,
        path: str
    ) -> Optional[ManifestLevel]:
        digger = self.tools.diggers.from_manifest(manifest)

        for step in path.split('/'):
            if not digger.has_sublevel(step):
                return None

            digger.delve_into(step)

        return digger.current_level

    def _preprocess_path(self, path: str) -> str:
        return path
