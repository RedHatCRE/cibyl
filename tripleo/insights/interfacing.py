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
from typing import List

from overrides import overrides

from tripleo.insights.types import URL, Path
from tripleo.utils.git.utils import get_repository_fullname
from tripleo.utils.github import GitHub
from tripleo.utils.github.pygithub import PyGitHub
from tripleo.utils.urls import is_git, is_github


class GitDownloader(ABC):
    def __init__(self, repository: URL):
        self._repository = repository

    @property
    def repository(self):
        return self._repository

    @abstractmethod
    def download_as_text(self, file: Path) -> str:
        raise NotImplementedError


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
    def download_as_text(self, file: Path) -> str:
        owner = self._get_repository_owner()
        name = self._get_repository_name()

        return self.api.get_repository(owner, name).download_as_text(file)

    def _get_repository_owner(self) -> str:
        return get_repository_fullname(self.repository).split('/')[0]

    def _get_repository_name(self) -> str:
        return get_repository_fullname(self.repository).split('/')[1]


def get_downloaders_for(url: URL) -> List[GitHubDownloader]:
    result = []

    if is_git(url):
        if is_github(url):
            result.append(GitHubDownloader(url))

        # Add a generic git handler here

    return result
