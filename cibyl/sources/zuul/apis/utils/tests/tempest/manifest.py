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
"""Represents a directory on the manifest."""


class ManifestDigger:
    """Tool used to transverse the directory tree of a manifest file. The
    purpose of this tool is to be able to safely go down a branch on the
    manifest's directory tree to its end. It allows to either observe the
    contents of a level or to go deeper down the line. Once the end is
    reached, this provides mechanism to be aware of so.
    """

    def __init__(self, manifest: Manifest):
        """Constructor.

        :param manifest: The manifest to dig through.
        """
        self._manifest = manifest
        self._current_level = manifest.tree

    @property
    def manifest(self) -> Manifest:
        """
        :return: The manifest this is working with.
        """
        return self._manifest

    @property
    def current_level(self) -> ManifestLevel:
        """
        :return: Contents of the level the digger is currently at.
        """
        return self._current_level

    def has_sublevel(self, name: str) -> bool:
        """Checks whether there is a directory below this level with the
        suggested name.

        :param name: The name to check.
        :return: True if there is, False if not.
        """
        return bool(self._get_sublevel(name))

    def delve_into(self, level: str) -> None:
        """Moves the digger down another level.

        .. seealso::
            :py:meth:`has_sublevel`
                -> For checking if the level exists beforehand.

        :param level: Name of the directory to go down to.
        :raises ArtifactError: If the level does not exist.
        """
        if not self.has_sublevel(level):
            msg = f"Manifest has no level: '{level}'."
            raise ArtifactError(msg)

        self._current_level = self._get_sublevel(level)

    def _get_sublevel(self, level: str) -> Optional[ManifestLevel]:
        """Gets the contents of a directory pending from the current level.

        :param level: Name of the directory to search for.
        :return: Contents of that directory. 'None' if it does not exist or
            the name points to a file instead.
        """
        # Search for the sublevel
        for item in self.current_level:
            # Does the sublevel exist?
            if item.name != level:
                continue

            # Check if at the end of the branch
            if not item.children:
                return None

            # Not yet at the end -> Return the new level then
            return item.children

        return None


class ManifestDiggerFactory:
    """Factory for `ManifestDigger`.
    """

    def from_manifest(self, manifest: Manifest) -> ManifestDigger:
        """Builds a new instance from a manifest file.

        :param manifest: The manifest that the digger will work with.
        :return: The digger's instance.
        """
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
