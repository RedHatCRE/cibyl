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
import tempfile
from abc import ABC, abstractmethod
from typing import Iterable

from overrides import overrides

from tripleo.utils.git import Git, Repository
from tripleo.utils.git.gitpython import GitPython
from tripleo.utils.git.utils import get_repository_fullname
from tripleo.utils.github import GitHub
from tripleo.utils.github.pygithub import PyGitHub
from tripleo.utils.types import URL, Path, Dir
from tripleo.utils.urls import is_git, is_github


class GitDownloader(ABC):
    def __init__(self, repository: URL):
        self._repository = repository

    @property
    def repository(self):
        return self._repository

    @abstractmethod
    def download_as_text(self, file: str) -> str:
        raise NotImplementedError


class GitCLIDownloader(GitDownloader):
    def __init__(
        self,
        repository: URL,
        working_dir: Dir,
        api: Git = GitPython()
    ):
        super().__init__(repository)

        self._api = api
        self._working_dir = working_dir

    @property
    def api(self):
        return self._api

    @property
    def working_dir(self):
        return self._working_dir

    @overrides
    def download_as_text(self, file: str) -> str:
        return self._get_repo().get_as_text(file)

    def _get_repo(self) -> Repository:
        if self.working_dir.is_empty():
            return self.api.clone(self.repository, self.working_dir)

        return self.api.open(self.working_dir)


class GitHubDownloader(GitDownloader):
    def __init__(
        self,
        repository: URL,
        api: GitHub = PyGitHub.from_no_login()
    ):
        super().__init__(repository)

        self._api = api

    @property
    def api(self) -> GitHub:
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
    DEFAULT_CLONE_PATH = Path('~/.cibyl')

    def __init__(self, clone_path: Path = DEFAULT_CLONE_PATH):
        self._clone_path = clone_path

    @property
    def clone_path(self):
        return self._clone_path

    def get_downloaders_for(self, url: URL) -> Iterable[GitHubDownloader]:
        result = []

        if is_git(url):
            if is_github(url):
                result.append(self._get_new_github_downloader(url))

            result.append(self._get_new_cli_downloader(url))

        return result

    def _get_new_cli_downloader(self, url: URL) -> GitCLIDownloader:
        return GitCLIDownloader(
            repository=url,
            working_dir=Dir(tempfile.mkdtemp(dir=self.clone_path))
        )

    def _get_new_github_downloader(self, url: URL) -> GitHubDownloader:
        return GitHubDownloader(repository=url)
