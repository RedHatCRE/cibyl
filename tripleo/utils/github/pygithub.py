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
from github import Github as GitHubAPIv3
from github import GithubException
from github.Repository import Repository as RepoAPIv3
from overrides import overrides

from tripleo.utils.github import GitHub as IGitHub
from tripleo.utils.github import GitHubError
from tripleo.utils.github import Repository as IRepository


class Repository(IRepository):
    """Implementation of the :class:`IRepository` using the PyGithub library as
    base.
    """

    def __init__(self, api: RepoAPIv3):
        """Constructor.

        :param api: PyGithub session used to interact with GitHub.
        """
        super().__init__(branch=api.default_branch)

        self._api = api

    @property
    def api(self) -> RepoAPIv3:
        """
        :return: API being in used to interact with GitHub.
        """
        return self._api

    @overrides
    def download_as_text(self, file: str, encoding: str = 'utf-8') -> str:
        try:
            file = self.api.get_contents(file, ref=self.branch)

            # Decoded content is still in binary,
            # it has to be passed to string yet
            return file.decoded_content.decode(encoding)
        except GithubException as ex:
            msg = f"Failed to fetch file at: '{file}'"
            raise GitHubError(msg) from ex


class PyGitHub(IGitHub):
    """Implementation of the :class:`IGitHub` using the PyGithub library as
    base.
    """

    def __init__(self, api: GitHubAPIv3):
        """Constructor.

        :param api: PyGithub session used to interact with GitHub.
        """
        self._api = api

    @property
    def api(self) -> GitHubAPIv3:
        """
        :return: API being in used to interact with GitHub.
        :rtype: :class:`GitHubAPIv3`
        """
        return self._api

    @staticmethod
    def from_no_login() -> 'PyGitHub':
        """Creates a new session without any login credentials. This will be
        able to access as much as a guest client is able to.

        :return: The instance.
        """
        return PyGitHub.from_login('', '')

    @staticmethod
    def from_login(user, password) -> 'PyGitHub':
        """Creates a new session with login credentials. This will be able to
        access as much as the logged-in user has access to.

        :return: The instance.
        """
        return PyGitHub(
            GitHubAPIv3(
                login_or_token=user,
                password=password
            )
        )

    @overrides
    def get_repository(self, owner: str, name: str) -> Repository:
        def full_name():
            return f'{owner}/{name}'

        try:
            repo = self.api.get_repo(full_name())

            return Repository(repo)
        except GithubException as ex:
            msg = f"Failed to fetch repository: '{full_name()}'"
            raise GitHubError(msg) from ex
