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

from tripleo.utils.urls import URL, is_git, is_github


class TestIsGit(TestCase):
    """Tests for :func:`is_git`.
    """

    def test_url_is_git(self):
        """Checks that true is returned if the URL points to a git
        repository.
        """
        url = URL('https://github.com/rhos-infra/cibyl.git')

        self.assertTrue(is_git(url))

    def test_url_is_not_git(self):
        """Checks that false if returned if the URL does not point to a git
        repository.
        """
        url = URL('http://localhost')

        self.assertFalse(is_git(url))


class TestIsGitHub(TestCase):
    """Tests for :func:`is_github`.
    """

    def test_url_is_github(self):
        """Checks that true is returned if 'github' is in the host name.
        """
        url = URL('https://github.com/rhos-infra/cibyl.git')

        self.assertTrue(is_github(url))

    def test_url_is_not_github(self):
        """Checks that false is returned if 'github' is not in the host
        name.
        """
        url = URL('http://localhost')

        self.assertFalse(is_github(url))
