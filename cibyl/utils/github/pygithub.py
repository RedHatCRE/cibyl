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
from github.Repository import Repository

from cibyl.utils.github import GitHub as IGitHub
from cibyl.utils.github import Repository as IRepository

RepoAPIv3 = Repository


class Repository(IRepository):
    def __init__(self, api):
        """

        :param api:
        :type api: :class:`RepoAPIv3`
        """
        self._api = api

    @property
    def api(self):
        return self._api

    def download_file(self, path, encoding='utf-8'):
        file = self._api.get_contents(path)

        # Decoded content is still in binary, it has to be passed to string yet
        return file.decoded_content.decode(encoding)


class PyGitHub(IGitHub):
    def __init__(self, api):
        """

        :param api:
        :type api: :class:`GitHubAPIv3`
        """
        self._api = api

    @property
    def api(self):
        return self._api

    @staticmethod
    def from_login(user, password):
        return PyGitHub(
            GitHubAPIv3(
                login_or_token=user,
                password=password
            )
        )

    def get_repository(self, owner, name):
        def full_name():
            return f'{owner}/{name}'

        api = self._api.get_repo(full_name())

        return Repository(api)
