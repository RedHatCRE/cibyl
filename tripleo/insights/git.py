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
from typing import Sequence

from overrides import overrides

from tripleo.utils.git import Git, Repository
from tripleo.utils.git.gitpython import GitPython
from tripleo.utils.git.utils import get_repository_fullname
from tripleo.utils.github import GitHub
from tripleo.utils.github.pygithub import PyGitHub
from tripleo.utils.types import URL, Dir
from tripleo.utils.urls import is_git, is_github


class GitDownloader(ABC):
    """Utility that makes it easy to access files on a Git repository.

    This will handle all the boilerplate needed to get to a file
    on a Git repository so that the user can leave all of that out and
    concentrate on what they need.
    """

    def __init__(self, repository: URL):
        """Constructor.

        :param repository: URL to the Git repository.
        """
        self._repository = repository

    @property
    def repository(self):
        """
        :return: URL to the Git repository.
        """
        return self._repository

    @abstractmethod
    def download_as_text(self, file: str) -> str:
        """

        :param file: Relative path to the repository's root pointing to the
            file to be downloaded.
        :return: Contents of that file.
        :raises DownloadError: If the file could not be downloaded.
        """
        raise NotImplementedError


class GitCLIDownloader(GitDownloader):
    """Implements the 'GitDownloader' interface through the use of the Git CLI.

    Have in mind that this will need to clone the Git repository and, thus,
    will affect the filesystem.
    """

    def __init__(
        self,
        repository: URL,
        working_dir: Dir,
        api: Git = GitPython()
    ):
        """Constructor.

        :param repository: URL to the Git repository.
        :param working_dir: Directory where the repository will get cloned in.
        :param api: API used to interact with the Git CLI.
        """
        super().__init__(repository)

        self._api = api
        self._working_dir = working_dir

    @property
    def api(self) -> Git:
        """
        :return: API used to interact with the Git CLI.
        """
        return self._api

    @property
    def working_dir(self) -> Dir:
        """
        :return: Directory where the repository will get cloned in.
        """
        return self._working_dir

    @overrides
    def download_as_text(self, file: str) -> str:
        return self._get_repo().get_as_text(file)

    def _get_repo(self) -> Repository:
        # Check if the repository is present on the filesystem
        if self.working_dir.is_empty():
            # Download it then
            return self.api.clone(self.repository, self.working_dir)

        # Being it already here, let's try to reuse it
        return self.api.open(self.working_dir)


class GitHubDownloader(GitDownloader):
    """Implements the 'GitDownloader' interface through the use of the GitHub
    API.
    """

    def __init__(
        self,
        repository: URL,
        api: GitHub = PyGitHub.from_no_login()
    ):
        """Constructor.

        :param repository: URL to the Git repository.
        :param api: API to interact with GitHub.
        """
        super().__init__(repository)

        self._api = api

    @property
    def api(self) -> GitHub:
        """
        :return: API to interact with GitHub.
        """
        return self._api

    @overrides
    def download_as_text(self, file: str) -> str:
        owner = self._get_repository_owner()
        name = self._get_repository_name()

        repo = self.api.get_repository(owner, name)

        return repo.download_as_text(file)

    def _get_repository_owner(self) -> str:
        return get_repository_fullname(self.repository).split('/')[0]

    def _get_repository_name(self) -> str:
        return get_repository_fullname(self.repository).split('/')[1]


class GitDownloaderFetcher:
    """Tool used to find the downloaders that are compatible with a certain
    URL.
    """
    DEFAULT_CLONE_PATH = Dir('~/.cibyl')
    """Default directory where Git repositories are cloned to if needed."""

    def __init__(self, clone_path: Dir = DEFAULT_CLONE_PATH):
        """
        :param clone_path: Directory where Git repositories are cloned in if
            required.
        """
        self._clone_path = clone_path

    @property
    def clone_path(self) -> Dir:
        """
        :return: Directory where Git repositories are cloned in if required.
        """
        return self._clone_path

    def get_downloaders_for(self, url: URL) -> Sequence[GitHubDownloader]:
        """
        :param url: URL to test.
        :return: List of downloaders that can provide support
            for the tested URL, ordered from most preferred to least.
            Can also be empty.
        """
        result = []

        if is_git(url):
            if is_github(url):
                result.append(self._get_new_github_downloader(url))

            result.append(self._get_new_cli_downloader(url))

        return result

    def _get_new_cli_downloader(self, url: URL) -> GitCLIDownloader:
        return GitCLIDownloader(repository=url, working_dir=self.clone_path)

    def _get_new_github_downloader(self, url: URL) -> GitHubDownloader:
        return GitHubDownloader(repository=url)
