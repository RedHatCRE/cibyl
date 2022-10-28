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
from unittest.mock import Mock

from kernel.scm.tools.fs import WorkspaceFactory
from kernel.tools.fs import Dir


class TestWorkspaceFactory(TestCase):
    """Tests for :class:`WorkspaceFactory`.
    """

    def test_new_workspace(self):
        """Checks that it creates a new directory under the root and
        returns it.
        """
        folder = '1234'

        folders = Mock()
        folders.new_name = Mock()
        folders.new_name.return_value = folder

        with TemporaryDirectory() as root:
            factory = WorkspaceFactory(
                root=Dir(root),
                tools=WorkspaceFactory.Tools(
                    folders=folders
                )
            )

            workspace = factory.new_workspace()

            self.assertEqual(f'{root}/{folder}', workspace)
            self.assertTrue(workspace.exists())
            self.assertTrue(workspace.is_empty())
