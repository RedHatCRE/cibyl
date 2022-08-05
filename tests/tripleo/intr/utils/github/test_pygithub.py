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

from tripleo.utils.github import GitHubError
from tripleo.utils.github.pygithub import PyGitHub


class TestPyGitHub(TestCase):
    """Tests for :class:`PyGitHub`.
    """

    def test_error_on_unknown_repo(self):
        """Checks that the correct error type is thrown in case the
        repository could not be fetched.
        """
        github = PyGitHub.from_no_login()

        with self.assertRaises(GitHubError):
            github.get_repository('some_owner', 'some_repo')

    def test_error_on_unknown_file(self):
        """Checks that the correct error type is thrown in case the file to
        download could not be found.
        """
        github = PyGitHub.from_no_login()
        repo = github.get_repository('rhos-infra', 'cibyl')

        with self.assertRaises(GitHubError):
            repo.download_as_text('some_file')

    def test_downloads_file_as_text(self):
        """Checks that it is possible to download a file through the API."""
        github = PyGitHub.from_no_login()
        repo = github.get_repository('rhos-infra', 'cibyl')
        result = repo.download_as_text('README.rst')

        with open('README.rst', 'r') as readme:
            self.assertEquals(result, readme.read())
