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

    @abstractmethod
    def download_as_text(self, file):
        """Downloads a file and decodes it as text.

        :param file: Relative path to the file starting from the
            repository's root.
        :type file: str
        :return: Text in the file.
        :rtype: str
        :raises GitHubError: If the file could not be downloaded.
        """
        raise NotImplementedError


class GitHub(ABC):
    """API that allows interactivity with GitHub.
    """

    @abstractmethod
    def get_repository(self, owner, name):
        """Fetches the repository and creates a session to allow
        interactivity with it.

        Examples
        ========
        >>> gh.get_repository('rhos-infra', 'cibyl')

        :param owner: Owner of the repository.
        :type owner: str
        :param name: Name of the repository.
        :type name: str
        :return: API to interact with the repository.
        :rtype: :class:`Repository`
        :raises GitHubError: If the repository could not be accessed.
        """
        raise NotImplementedError
