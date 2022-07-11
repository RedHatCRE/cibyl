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

from tripleo.utils.fs import Dir
from tripleo.utils.io import Closeable
from tripleo.utils.urls import URL


class GitError(Exception):
    """Describes any errors occurring while interacting with Git's CLI.
    """


class Repository(Closeable, ABC):
    @abstractmethod
    def get_as_text(self, file: str, encoding: str = 'utf-8') -> str:
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
