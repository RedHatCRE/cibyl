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
import logging
import os
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union

LOG = logging.getLogger(__name__)


class FileSearch:
    """Allows for complex search queries targeting files on the filesystem.
    """

    @dataclass
    class SearchTerms:
        """Set of modifiers to condition the search.
        """
        recursive: bool = field(default_factory=lambda *_: False)
        """Whether the search should iterate over sub-directories."""
        excluded: List[str] = field(default_factory=lambda *_: [])
        """Name of files to remove from the result."""
        extensions: List[str] = field(default_factory=lambda *_: [])
        """Dot-Prefixed extensions to look for, e.g.: '.py'."""

    def __init__(self, directory: str, terms: Optional[SearchTerms] = None):
        """Constructor.

        :param directory:
            Path to directory to look for files in.
        :param terms:
            Preset of search terms used when looking for files.
            'None' to begin from an empty state.
        """
        if terms is None:
            terms = FileSearch.SearchTerms()

        self._directory = directory
        self._terms = terms

    def with_recursion(self) -> 'FileSearch':
        """Extends the search to the folders inside the directory and beyond.

        :return: The instance.
        """
        self._terms.recursive = True
        return self

    def with_extension(self, extension: str) -> 'FileSearch':
        """Limits the search to files of a certain extensions. If this is
        called more than once, then the filters are joined together following
        and 'OR' approach.

        :param extension: The extension to filter by, dot-prefixed: '.py'.
        :return: The instance.
        """
        self._terms.extensions.append(extension)
        return self

    def with_excluded(self, excluded: List[str]) -> 'FileSearch':
        """Limits the search to files that are not in the excluded list. If
        this is called more than once, then the filters are joined together
        following an 'OR' approach.

        :param excluded: The file names to filter by.
        :return: The instance.
        """
        self._terms.excluded.extend(excluded)
        return self

    def get(self) -> List[str]:
        """Performs the query and gets the paths to the files that were
        found by the search.

        :return: Paths to the files.
        """

        def list_directory() -> List[str]:
            return [
                f'{self._directory}/{entry}'
                for entry in os.listdir(self._directory)
            ]

        result = []

        for path in list_directory():
            if os.path.isdir(path):
                if self._terms.recursive:
                    result += self._copy_for(path).get()
            else:
                if self._terms.extensions:
                    if get_file_extension(path) not in self._terms.extensions:
                        continue
                if self._terms.excluded:
                    if get_file_name_from_path(path) in self._terms.excluded:
                        continue

                result.append(path)

        return result

    def _copy_for(self, directory: str) -> 'FileSearch':
        """Makes a copy of this search intended for another directory. The
        resulting search will follow the same filters as this one, making
        the resulting files follow the same rules.

        :param directory: The directory to search this time around.
        :return: The search's instance.
        """
        return FileSearch(
            directory=directory,
            terms=self._terms
        )


class FileSearchFactory:
    """Factory for :class:`FileSearch`.
    """

    def from_root(self, root: str):
        """Builds a new search that begins from the given root directory.

        :param root: Path to directory to look files in.
        :return: The instance.
        """
        return FileSearch(directory=root)


def is_file_available(filename: str) -> bool:
    """Checks if a file is present on the filesystem.

    :param filename: A path pointing to the file to be checked.
    :return: Whether the file is there or not.
    """
    return os.path.isfile(filename)


def get_first_available_file(
    filenames: Iterable[Union[bytes, str, PathLike]],
    file_check: Callable[[str], bool] = is_file_available
) -> Union[bytes, str, None]:
    """Searches for the first file out of the provided paths that exists
    on the host's drive.

    :param filenames: A list of paths pointing to different files.
    :param file_check: A function that determines if a file is present.
    :return: A string containing the path to the found file. 'None' if no
        file is available
    """
    for filename in filenames:
        # Resolve path into a string
        if isinstance(filename, PathLike):
            filename = os.fspath(filename)

        # Check if file exists
        if file_check(filename):
            return filename

        LOG.debug('%s: %s', 'file not found', filename)

    # None of the files exist
    return None


def get_file_name_from_path(path: str) -> str:
    """Get the file name from a path. Strip all leading path
    information as well as the extension.
    :param path: Path of the file
    :returns: The name of the file that path points to, without extension
    """
    path = path.replace("\\", os.sep)
    _, file_name = os.path.split(path)
    return os.path.splitext(file_name)[0]


def get_file_extension(path: str) -> str:
    """Gets the dot-prefixed extension from the path to a file.

    :param path: Path to the file to get the extension from.
    :return: The file's extension.

    Examples
    --------
    >>> get_file_extension('/home/user/file.txt')
    '.txt'
    """
    return Path(path).suffix
