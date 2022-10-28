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
from unittest.mock import Mock, patch

from kernel.scm.tools.fs import UUIDFactory, WorkspaceFactory


class TestUUIDFactory(TestCase):
    """Tests for :class:`UUIDFactory`.
    """

    @patch('kernel.scm.tools.fs.get_new_uuid')
    def test_calls_generator(self, uuids: Mock):
        """Checks that the factory uses the expected UUID generator.
        """
        uuid = '1234'
        uuids.return_value = uuid

        factory = UUIDFactory()

        self.assertEqual(uuid, factory.new_name())


class TestWorkspaceFactory(TestCase):
    """Tests for :class:`WorkspaceFactory`.
    """

    def test_new_workspace(self):
        """Checks that the correct steps are taken to create a new
        workspace.
        """
        root = Mock()
        folders = Mock()

        folder = Mock()
        workspace = Mock()

        folders.new_name = Mock()
        folders.new_name.return_value = folder

        root.cd = Mock()
        root.cd.return_value = workspace

        workspace.mkdir = Mock()

        factory = WorkspaceFactory(
            root=root,
            tools=WorkspaceFactory.Tools(
                folders=folders
            )
        )

        self.assertEqual(workspace, factory.new_workspace())

        folders.new_name.assert_called_once()
        root.cd.assert_called_once_with(path=folder)
        workspace.mkdir.assert_called_once_with(recursive=True)
