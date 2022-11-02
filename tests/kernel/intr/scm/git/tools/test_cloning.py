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
            self.assertIn(folder, result.workspace)

    def test_opens_repository(self):
        """Checks that once cloned, the factory can open a repository for
        its session.
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

            result1 = repositories.from_remote(url)
            remotes1 = [remote.urls for remote in result1.remotes]
            workspace1 = result1.workspace

            result2 = repositories.from_remote(url)
            remotes2 = [remote.urls for remote in result2.remotes]
            workspace2 = result2.workspace

            self.assertEqual(remotes1, remotes2)
            self.assertEqual(workspace1, workspace2)

    def test_retries_somewhere_else(self):
        """Checks that if a repository cannot be opened, then it is cloned
        again somewhere else.
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

            result1 = repositories.from_remote(url)
            remotes1 = [remote.urls for remote in result1.remotes]
            workspace1 = result1.workspace

            result1.workspace.rm()

            result2 = repositories.from_remote(url)
            remotes2 = [remote.urls for remote in result2.remotes]
            workspace2 = result2.workspace

            self.assertEqual(remotes1, remotes2)
            self.assertNotEqual(workspace1, workspace2)
