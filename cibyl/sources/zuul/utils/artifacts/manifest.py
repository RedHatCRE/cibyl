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
from typing import Iterable, List, NamedTuple, Optional, Sequence, Tuple

from xsdata.formats.dataclass.parsers import JsonParser

from cibyl.sources.zuul.apis import Artifact, ArtifactKind
from cibyl.sources.zuul.apis.http import ZuulHTTPBuildAPI as Build
from cibyl.sources.zuul.utils.artifacts import ArtifactError
from cibyl.utils.filtering import matches_regex
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
        :raises ArtifactError: If the build has no manifest or exposes
                more than one.
        """
        downloader = ManifestDownloader.DownloadFromBuild(build, self.tools)

        return downloader.get_manifest()


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


class ManifestDir(str):
    """Represents a path to a directory on a manifest file.
    """

    def __new__(cls, value: str) -> 'ManifestDir':
        """Constructor.

        The path is expected to be in a specific format for it to be
        accepted. Some valid examples of this format are as follows:
            - '/' -> Root of the manifest
            - '/var/logs/tempest' -> A directory some levels deep

        These other examples will not be accepted though:
            - '/home/zuul/' -> Trailing '/' is forbidden
            - 'home/logs' -> Must begin with a '/' character

        :param value: The path to the directory.
        :raises ValueError: If the path's format is invalid.
        """
        if not matches_regex(r'^(\/|(\/\w+)+)$', value):
            raise ValueError(f"Invalid format for manifest path: '{value}'.")

        return super().__new__(cls, value)


class ManifestFile(str):
    """Represents a path to a file on manifest file.
    """

    def __new__(cls, value: str) -> 'ManifestFile':
        """Constructor.

        The path is expected to be in a specific format for it to be
        accepted. Some valid examples of this format are as follows:
            - '/file.txt' -> File at the root of the manifest
            - '/var/logs/tempest/results.xml' -> File on a subdir

        These other examples will not be accepted though:
            - 'home/file.txt' -> Must begin with a '/' character
            - '/var/logs/file' -> Must have an extension

        :param value: The path to the file.
        :raises ValueError: If the path's format is invalid.
        """
        if not matches_regex(r'^(\/\w+)*(\/\w*\.\w*)$', value):
            raise ValueError(f"Invalid format for manifest path: '{value}'.")

        return super().__new__(cls, value)


class ManifestFileSearch:
    """Tool used to search for a certain file across a manifest's tree.
    """

    class SearchTerms(NamedTuple):
        """Defines what the class has to search for.
        """
        paths: Iterable[ManifestDir]
        """Collection of paths where the desired file may be. The class will
        iterate through these in search of one of the desired files."""
        files: Iterable[str]
        """Collection of names the desired file may take. The class will
        iterate through these at each path until one of them is found. The
        first to be will be the one to be returned. Each of the files added
        here must have an extension."""

    class Tools(NamedTuple):
        """Tools this uses to do its job.
        """
        diggers: ManifestDiggerFactory = ManifestDiggerFactory()
        """Creates the walkers that will allow this to transverse the tree."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: The tools this will use to do its job.
        """
        self._tools = tools

    @property
    def tools(self):
        """
        :return: The tools this will use to do its job.
        """
        return self._tools

    def find_in(
        self,
        manifest: Manifest,
        search_terms: SearchTerms
    ) -> Optional[Tuple[ManifestFile, ManifestItem]]:
        """Searches the manifest file for the element defined in the search
        terms.

        :param manifest: The manifest file to search in.
        :param search_terms: Defines what this will need to search for.
        :return: A tuple containing on its first element the path to the file
            and on its second the manifest entry that represents it. 'None'
            if nothing were found.
        """
        for path in search_terms.paths:
            level = self._get_manifest_level(manifest, path)

            if not level:
                # The file's directory does not exist
                continue

            for file in search_terms.files:
                # See if the file is at this level
                item = next(
                    (item for item in level if item.name == file),
                    None
                )

                if not item:
                    # The file is not here
                    continue

                # Generate path to the file
                return self._from_dir_to_file(path, file), item

        return None

    def _get_manifest_level(
        self,
        manifest: Manifest,
        path: ManifestDir
    ) -> Optional[ManifestLevel]:
        """
        :param manifest: The manifest to go through.
        :param path: Path to the directory to get.
        :return: Contents of the directory indicated by them. 'None' if the
            directory could not be reached.
        """
        digger = self.tools.diggers.from_manifest(manifest)

        for step in self._split_path(path):
            if not digger.has_sublevel(step):
                return None

            digger.delve_into(step)

        return digger.current_level

    def _split_path(self, path: ManifestDir) -> Iterable[str]:
        """
        :param path: The path to divide.
        :return: An ordered collection containing the names of the folders
            that need to be cd'd in order to get to the one marked by the path.
        """
        # Remove initial '/' to avoid empty splits
        return path[1:].split('/')

    def _from_dir_to_file(self, path: ManifestDir, file: str) -> ManifestFile:
        result = path

        # In case it is not the manifest's root
        if not result.endswith('/'):
            result += '/'

        result += file

        return ManifestFile(result)
