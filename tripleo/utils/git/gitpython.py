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
import logging
import os
from typing import Iterable

from git import InvalidGitRepositoryError, NoSuchPathError
from git import Remote as RemoteAPI
from git import Repo as RepoAPI
from overrides import overrides

from tripleo.utils.fs import Dir, File
from tripleo.utils.git import Git as IGit
from tripleo.utils.git import GitError
from tripleo.utils.git import Remote as IRemote
from tripleo.utils.git import Repository as IRepository
from tripleo.utils.urls import URL

LOG = logging.getLogger(__name__)


class Remote(IRemote):
    """Implementation of a Git CLI interface with the use of the GitPython
    library.
    """

    def __init__(self, handler: RemoteAPI):
        """Constructor.

        :param handler: An API to interact with the remote.
        """
        self._handler = handler

    @property
    def handler(self) -> RemoteAPI:
        """
        :return: API used to interact with the remote.
        """
        return self._handler

    @property
    def name(self) -> str:
        return self.handler.name

    @property
    def urls(self) -> Iterable[URL]:
        return [URL(url) for url in self.handler.urls]


class Repository(IRepository):
    """Implementation of a Git CLI interface with the use of the GitPython
    library.
    """

    def __init__(self, handler: RepoAPI):
        """Constructor.

        :param handler: An open session to the repository.
        """
        self._handler = handler

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @property
    def handler(self) -> RepoAPI:
        """
        :return: Session used to interact with the repository.
        """
        return self._handler

    @property
    def branch(self) -> str:
        return self.handler.active_branch.name

    @property
    def remotes(self) -> Iterable[Remote]:
        return [Remote(remote) for remote in self.handler.remotes]

    @overrides
    def checkout(self, branch: str) -> None:
        remote = self.handler.remote()

        # Check that the branch exists.
        if branch not in remote.refs:
            raise GitError(f"Unknown branch: '{branch}'")

        self.handler.git.checkout(branch)

    @overrides
    def get_as_text(self, file: str, encoding: str = 'utf-8') -> str:
        abs_path = self._get_absolute_path(file)

        try:
            with open(abs_path, 'r', encoding=encoding) as buffer:
                return buffer.read()
        except IOError as ex:
            msg = f"Failed to open file at: '{abs_path}'."
            raise GitError(msg) from ex

    @overrides
    def close(self):
        self.handler.close()

    def _get_absolute_path(self, file: str) -> str:
        """
        :param file: Relative path to a file inside the repository.
        :return: Absolute path to such file.
        """
        path = os.path.join(self.handler.working_dir, file)
        path = os.path.abspath(path)

        return File(path)


class GitPython(IGit):
    """Implementation of a Git CLI interface with the use of the GitPython
    library.
    """

    @overrides
    def open(self, working_dir: Dir) -> Repository:
        try:
            LOG.info("Opening repository at: '%s'.", working_dir)
            repo = RepoAPI(working_dir.as_path())
            return Repository(repo)
        except InvalidGitRepositoryError as ex:
            msg = f"Failed to open repository at: '{working_dir}'."
            raise GitError(msg) from ex
        except NoSuchPathError as ex:
            msg = f"Could not open directory: '{working_dir}'."
            raise GitError(msg) from ex

    @overrides
    def clone(self, url: URL, working_dir: Dir) -> Repository:
        LOG.info("Cloning repository: '%s' into: '%s'.", url, working_dir)
        repo = RepoAPI.clone_from(url, working_dir.as_path())
        return Repository(repo)
