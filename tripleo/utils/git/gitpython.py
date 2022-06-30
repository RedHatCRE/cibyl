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

from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from overrides import overrides

from tripleo.utils.git import Git as IGit, GitError
from tripleo.utils.git import Repository as IRepository
from tripleo.utils.types import URL, Dir, File


class Repository(IRepository):
    """Implementation of a Git CLI interface with the use of the GitPython
    library.
    """

    def __init__(self, handler: Repo):
        """Constructor.

        :param handler: An open session to the repository.
        """
        self._handler = handler

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @property
    def handler(self) -> Repo:
        """
        :return: Session used to interact with the repository.
        """
        return self._handler

    @overrides
    def get_as_text(self, file: str) -> str:
        abs_path = self._get_absolute_path(file)

        try:
            with open(abs_path, 'r') as buffer:
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

        return File(path).absolute()


class GitPython(IGit):
    """Implementation of a Git CLI interface with the use of the GitPython
    library.
    """

    @overrides
    def open(self, working_dir: Dir) -> Repository:
        try:
            repo = Repo(working_dir.as_path())

            return Repository(repo)
        except InvalidGitRepositoryError as ex:
            msg = f"Failed to open repository at: '{working_dir}'."
            raise GitError(msg) from ex
        except NoSuchPathError as ex:
            msg = f"Could not open directory: '{working_dir}'."
            raise GitError(msg) from ex

    @overrides
    def clone(self, url: URL, working_dir: Dir) -> Repository:
        repo = Repo.clone_from(url, working_dir.as_path())

        return Repository(repo)
