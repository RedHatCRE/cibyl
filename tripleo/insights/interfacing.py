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
from typing import Optional

from overrides import overrides

from tripleo.insights import URL, Path
from tripleo.utils.git.utils import get_repository_fullname
from tripleo.utils.github import GitHub, Repository
from tripleo.utils.github.pygithub import PyGitHub


class GitDownloader(ABC):
    def __init__(self, repository: URL):
        self._repository = repository

    @property
    def repository(self):
        return self._repository

    @abstractmethod
    def _setup(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_as_text(self, file: Path) -> str:
        raise NotImplementedError


class GitHubDownloader(GitDownloader):
    def __init__(self,
                 repository: URL,
                 api: GitHub = PyGitHub.from_no_login()):
        super().__init__(repository)

        self._github_api = api
        self._repo_api: Optional[Repository] = None

    @property
    def api(self) -> GitHub:
        return self._github_api

    @overrides
    def _setup(self) -> None:
        self._repo_api = self._github_api.get_repository(
            self._get_repository_owner(),
            self._get_repository_name()
        )

    @overrides
    def download_as_text(self, file: Path) -> str:
        return self._repo_api.download_file(file)

    def _get_repository_owner(self) -> str:
        return get_repository_fullname(self.repository).split('/')[0]

    def _get_repository_name(self) -> str:
        return get_repository_fullname(self.repository).split('/')[1]
