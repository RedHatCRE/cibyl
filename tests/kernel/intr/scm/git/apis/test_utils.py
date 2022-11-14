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

from kernel.scm.git.apis.utils import get_repository_fullname
from kernel.tools.urls import URL


class TestGetRepositoryFullname(TestCase):
    """Tests for :class:`get_repository_fullname`.
    """

    def test_gets_fullname(self):
        """Checks that the repository's fullname is retrieved if the URL
        points to a git repo.
        """
        url = URL('https://github.com/rhos-infra/cibyl.git')

        self.assertEqual('rhos-infra/cibyl', get_repository_fullname(url))
