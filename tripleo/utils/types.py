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
from abc import ABC
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Union

from tripleo.utils.strings import is_url

YAML = Dict[str, Any]
"""Represents data originated from reading a YAML file."""


class FSPath(ABC):
    """Base class for representations of a filesystem path. These are able
    to make system calls and are meant to model elements existing on the
    filesystem.
    """

    def __init__(self, path: Union[bytes, str, PathLike, Path]):
        """Constructor.

        :param path: Representation of the path to handle.
        """
        if not isinstance(path, Path):
            path = Path(path)

        self._path = path

    def __str__(self):
        return self.as_str()

    def absolute(self) -> str:
        """
        :return: An absolute version of this path.
        """
        return str(self.as_path().absolute())

    def as_str(self) -> str:
        """
        :return: The raw filesystem path itself.
        """
        return str(self.as_path())

    def as_path(self) -> Path:
        """
        :return: The path in pathlib format.
        """
        return self._path


class Dir(FSPath):
    """Represents a directory on the filesystem.
    """

    def __init__(self, path: Union[bytes, str, PathLike, Path]):
        """Constructor. See parent for more information.

        :raises ValueError: If the path does not exist or is not a directory.
        """
        super().__init__(path)

        if not self.as_path().is_dir():
            msg = f"Path is not a directory or does not exist: '{str(self)}'."
            raise ValueError(msg)

    def is_empty(self) -> bool:
        """
        :return: True if the directory has no files within, False otherwise.
        """
        return not any(self.as_path().iterdir())


class File(FSPath):
    """Represents a file on the filesystem.
    """

    def __init__(self, path: Union[bytes, str, PathLike, Path]):
        """Constructor. See parent for more information.

        :raises ValueError: If the path does not exist or is not a file.
        """
        super().__init__(path)

        if not self.as_path().is_file():
            msg = f"Path is not a file or does not exist: '{str(self)}'."
            raise ValueError(msg)


class URL(str):
    """Extension of a string to exclusively model URLs.
    """

    def __new__(cls, value: str) -> 'URL':
        """Constructor.

        The string is preprocessed a bit for convenience’ sake. Some actions
        taken are:
            - Trimming the string.

        :param value: The string's text.
        :raises ValueError: If the string does not follow a URL format.
        """
        # Avoid false positives by removing leading and trailing whitespaces
        value = value.strip()

        if not is_url(value):
            msg = f"String does not represent a valid URL: '{value}'."
            raise ValueError(msg)

        return super().__new__(cls, value)
