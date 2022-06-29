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
import os

from git import Repo
from overrides import overrides

from tripleo.insights.types import URL, Path
from tripleo.utils.git import Git as IGit
from tripleo.utils.git import Repository as IRepository


class Repository(IRepository):
    def __init__(self, handler: Repo):
        self._handler = handler

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @property
    def handler(self) -> Repo:
        return self._handler

    @overrides
    def get_as_text(self, file: Path) -> str:
        with open(self._get_absolute_path(file), 'r') as buffer:
            return buffer.read()

    @overrides
    def close(self):
        self.handler.close()

    def _get_absolute_path(self, file: Path) -> Path:
        return os.path.join(self.handler.working_dir, file)


class GitPython(IGit):
    @overrides
    def clone(self, url: URL, working_dir: Path) -> Repository:
        repo = Repo.clone_from(url, working_dir)

        return Repository(repo)
