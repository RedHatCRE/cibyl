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
from abc import ABC, abstractmethod
from typing import Iterable

from tripleo.utils.fs import Dir
from tripleo.utils.io import Closeable
from tripleo.utils.urls import URL


class GitError(Exception):
    """Describes any errors occurring while interacting with Git's CLI.
    """


class Remote(ABC):
    """Interface that defines interactions with a Git remote.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: Name of the remote.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def urls(self) -> Iterable[URL]:
        """
        :return: URLs the remote pulls from/pushes to.
        """
        raise NotImplementedError


class Repository(Closeable, ABC):
    """Interface that defines interactions with a Git repository.
    """

    @property
    @abstractmethod
    def branch(self) -> str:
        """
        :return: The active branch on the repository.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def remotes(self) -> Iterable[Remote]:
        """
        :return: Collection of remotes the repository works with.
        """
        raise NotImplementedError

    @abstractmethod
    def checkout(self, branch: str) -> None:
        """Changes the active branch on the repository.

        :param branch: Name of the branch to move to.
        :raises GitError: If the branch does not exist.
        """
        raise NotImplementedError

    @abstractmethod
    def get_as_text(self, file: str, encoding: str = 'utf-8') -> str:
        """Downloads a file on the repository as text.

        :param file: Path, relative to the repository's root, to the file
            to download.
        :param encoding: Encoding of the file, following the same naming as the
            builtin 'open' function.
        :return: The contents of the file as text.
        """
        raise NotImplementedError


class Git(ABC):
    """Interface that defines interactions with the Git CLI.
    """

    @abstractmethod
    def open(self, working_dir: Dir) -> Repository:
        """Open a Git repository located on the filesystem.

        :param working_dir: The directory where the repository is at.
        :return: A handler to interact with the repository.
        :raises GitError: If the repository could not be opened.
        """
        raise NotImplementedError

    @abstractmethod
    def clone(self, url: URL, working_dir: Dir) -> Repository:
        """Clones a repository from a remote host into the local filesystem.

        :param url: URL to the repository.
        :param working_dir: Where the repository will be cloned into.
        :return: A handler to interact with the repository.
        :raises GitError: If the repository could not be cloned.
        """
        raise NotImplementedError
