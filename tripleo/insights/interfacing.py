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

from tripleo.insights import URL, Path


class GitDownloader(ABC):
    def __init__(self, repository: URL):
        self._repository = repository

    @property
    def repository(self):
        return self._repository

    @abstractmethod
    def _setup(self):
        raise NotImplementedError

    @abstractmethod
    def download_as_text(self, file: Path) -> str:
        raise NotImplementedError


class GitHubDownloader(GitDownloader):


    def _setup(self):
        pass

    def download_as_text(self, file: Path) -> str:
        pass
