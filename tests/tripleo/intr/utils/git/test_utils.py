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

from tripleo.utils.git.utils import get_repository_fullname
from tripleo.utils.urls import URL


class TestGetRepositoryFullname(TestCase):
    """Tests for :class:`get_repository_fullname`.
    """

    def test_error_if_not_git_url(self):
        """Checks that an error is raised if the URL does not point
        to a git repository.
        """
        url = URL('http://localhost')

        with self.assertRaises(ValueError):
            get_repository_fullname(url)

    def test_gets_fullname(self):
        """Checks that the repository's fullname is retrieved if the URL
        points to a git repo.
        """
        url = URL('https://github.com/rhos-infra/cibyl.git')

        self.assertEqual('rhos-infra/cibyl', get_repository_fullname(url))
