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
from tempfile import TemporaryDirectory
from unittest import TestCase

from kernel.scm.git.tools.cloning import RepositoryFactory
from kernel.scm.tools.fs import WorkspaceFactory
from kernel.tools.fs import Dir
from kernel.tools.urls import URL


class TestRepositoryFactory(TestCase):
    """Tests for :class:`RepositoryFactory`.
    """

    def test_clones_repository(self):
        """Checks that the factory is capable of creating a new session by
        cloning the repository.
        """
        url = URL('https://github.com/RedHatCRE/cibyl.git')

        with TemporaryDirectory() as folder:
            repositories = RepositoryFactory(
                tools=RepositoryFactory.Tools(
                    workspaces=WorkspaceFactory(
                        root=Dir(folder)
                    )
                )
            )

            result = repositories.from_remote(url)

            self.assertIn(url, *[remote.urls for remote in result.remotes])
