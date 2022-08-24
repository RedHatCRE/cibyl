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
import shutil
from abc import ABC, abstractmethod
from contextlib import contextmanager
from os import PathLike, chdir, getcwd
from pathlib import Path
from typing import Generator, Union

from overrides import overrides

from tripleo.utils.paths import Preprocessor

RawPath = Union[bytes, str, PathLike, Path]


@contextmanager
def cd_context_manager(path: RawPath) -> Generator:
    """Simple context manager that changes the working directory and restores
    the previous one on exit"""
    old_dir = getcwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(old_dir)


class FSPath(str, ABC):
    """Base class for representations of a filesystem path. These are able
    to make system calls and are meant to model elements existing on the
    filesystem.
    """

    def __new__(cls, value: RawPath, *makeup: Preprocessor):
        """Constructor.

        :param value: The path to build this from.
        :param makeup: Modifications applied to the path before it is
            converted into this type. 'value' is left untouched during this
            process.
        """
        result = Path(value)

        for cosmetic in makeup:
            result = cosmetic(result)

        return super().__new__(cls, str(result))

    @abstractmethod
    def check_exists(self) -> None:
        """
        :raises IOError: If the path does not exist or is not in the
            correct format.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self) -> bool:
        """
        :return: True is the path exists on the filesystem, False otherwise.
        """
        raise NotImplementedError

    def as_path(self) -> Path:
        """
        :return: The path in pathlib format.
        """
        return Path(self)


class Dir(FSPath):
    """Represents a directory on the filesystem.
    """

    @overrides
    def check_exists(self) -> None:
        if not self.exists():
            msg = f"Path is not a directory or does not exist: '{self}'."
            raise IOError(msg)

    @overrides
    def exists(self) -> bool:
        return self.as_path().is_dir()

    def is_empty(self) -> bool:
        """Checks if the directory has any files within.

        If the directory does not exist, this will return False.

        :return: True if the directory has no files within, False otherwise.
        """
        if not self.exists():
            return False

        return not any(self.as_path().iterdir())

    def cd(self, path: RawPath) -> 'Dir':
        """Combines this path with the one passed as an argument. Useful to
        represent subdirectories.

        :param path: The path to append.
        :return: A new directory handler, pointing to the combined path.
        """
        return Dir(self.as_path() / path)

    def mkdir(self, recursive: bool = False) -> None:
        """Creates the directory on the filesystem.

        :param recursive: Whether to also create missing directories
            leading to this one or not.
        :raises FileNotFoundError: If the parents on the directory do not
            exist. Can only happen if 'recursive" is False.
        """
        self.as_path().mkdir(parents=recursive, exist_ok=True)

    def rm(self) -> None:
        """Deletes the directory and all its contents. Does nothing if the
        directory does not exist.
        """
        shutil.rmtree(self)


class File(FSPath):
    """Represents a file on the filesystem.
    """

    @overrides
    def check_exists(self) -> None:
        if not self.exists():
            msg = f"Path is not a file or does not exist: '{self}'."
            raise IOError(msg)

    @overrides
    def exists(self) -> bool:
        return self.as_path().is_file()
