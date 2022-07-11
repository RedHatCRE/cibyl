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
from unittest import TestCase
from unittest.mock import Mock

from tripleo.utils.github.pygithub import PyGitHub, Repository


class TestPyGitHub(TestCase):
    """Tests for :class:`PyGitHub`.
    """

    def test_get_repository(self):
        """Checks that an API to access the repository is returned.
        """
        owner = 'me'
        name = 'repo'

        repo = Mock()

        api = Mock()
        api.get_repo = Mock()
        api.get_repo.return_value = repo

        github = PyGitHub(api)

        self.assertEqual(repo, github.get_repository(owner, name).api)

        api.get_repo.assert_called_once_with(f'{owner}/{name}')


class TestRepository(TestCase):
    """Tests for :class:`Repository`.
    """

    def test_downloads_file_as_text(self):
        """Checks that it is capable of retrieving the text from a file.
        """
        encoding = 'utf-8'

        path = 'path/to/file'
        contents = 'file_contents'

        branch = 'master'

        file = Mock()
        file.decoded_content = bytes(contents, encoding)

        api = Mock()
        api.default_branch = branch
        api.get_contents = Mock()
        api.get_contents.return_value = file

        repo = Repository(api)

        self.assertEqual(
            contents,
            repo.download_as_text(path, encoding)
        )

        api.get_contents.assert_called_once_with(path, ref=branch)

    def test_downloads_from_custom_branch(self):
        """Checks that it is capable of retrieving the text from a file
        in a branch different from the default one.
        """
        encoding = 'utf-8'

        path = 'path/to/file'
        contents = 'file_contents'

        branch = 'branch'

        file = Mock()
        file.decoded_content = bytes(contents, encoding)

        api = Mock()
        api.default_branch = 'master'
        api.get_contents = Mock()
        api.get_contents.return_value = file

        repo = Repository(api)
        repo.checkout(branch)

        self.assertEqual(
            contents,
            repo.download_as_text(path, encoding)
        )

        api.get_contents.assert_called_once_with(path, ref=branch)
