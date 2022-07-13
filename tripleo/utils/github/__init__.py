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


class GitHubError(Exception):
    """Represents any error happening during an interaction with GitHub."""


class Repository(ABC):
    """API that allows interactivity with a GitHub repository.
    """

    def __init__(self, branch: str):
        """Constructor.

        :param branch: Name of the branch the repository is checked out at.
        """
        self._branch = branch

    @property
    def branch(self) -> str:
        """
        :return: Name of the checked out branch.
        """
        return self._branch

    def checkout(self, branch: str) -> None:
        """Changes the branch the repository works in.

        :param branch: The branch to move to.
        """
        self._branch = branch

    @abstractmethod
    def download_as_text(self, file: str, encoding: str = 'utf-8') -> str:
        """Downloads a file and decodes it as text.

        :param file: Relative path to the file starting from the
            repository's root.
        :param encoding: Encoding of the file, indicating just like in
            :func:`builtins.open`.
        :return: Text in the file.
        :raises GitHubError: If the file could not be downloaded.
        """
        raise NotImplementedError


class GitHub(ABC):
    """API that allows interactivity with GitHub.
    """

    @abstractmethod
    def get_repository(self, owner: str, name: str) -> Repository:
        """Fetches the repository and creates a session to allow
        interactivity with it.

        Examples
        ========
        >>> gh = GitHub()
        ... gh.get_repository('rhos-infra', 'cibyl')

        :param owner: Owner of the repository.
        :param name: Name of the repository.
        :return: API to interact with the repository.
        :raises GitHubError: If the repository could not be accessed.
        """
        raise NotImplementedError
