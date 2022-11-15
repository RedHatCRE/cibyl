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
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from overrides import overrides

from kernel.tools.fs import Dir
from kernel.tools.paths import resolve_home
from kernel.tools.rng import get_new_uuid

LOG = logging.getLogger(__name__)


class FolderNameFactory(ABC):
    """Base class for factories that generate random names for directories.
    """

    @abstractmethod
    def new_name(self) -> str:
        """Creates a new random name for a directory. Calling this multiple
        times will never produce the same name.

        :return: Not a path, but just the directory's name.
        """
        raise NotImplementedError


class UUIDFactory(FolderNameFactory):
    """Factory that generates directories by naming them after UUIDs.
    """

    @overrides
    def new_name(self) -> str:
        return get_new_uuid()


class WorkspaceFactory:
    """Factory that eases the creation of directories where SCM operations,
    such as cloning, can be performed in.
    """
    DEFAULT_ROOT = Dir('~/.cibyl', resolve_home)
    """Default location where the factory will 'mkdir' in."""

    @dataclass
    class Tools:
        """Tools this uses to perform its task.
        """
        folders: FolderNameFactory = field(
            default_factory=lambda *_: UUIDFactory()
        )
        """Generates names for the workspaces built by this."""

    def __init__(
        self,
        root: Optional[Dir] = None,
        tools: Optional[Tools] = None
    ):
        """Constructor.

        :param root: Directory where all built workspaces will hang from.
            This will never create files on the root, just directories. 'None'
            to go with the default one.
        :param tools: Tools this uses to perform its task. 'None' to let
            this build its own.
        """
        if root is None:
            root = WorkspaceFactory.DEFAULT_ROOT

            LOG.debug(
                "Root for workspaces not provided, defaulted to: '%s'.",
                root
            )

        if tools is None:
            tools = WorkspaceFactory.Tools()

        self._root = root
        self._tools = tools

    @property
    def root(self) -> Dir:
        """
        :return: Directory where all built workspaces will hang from.
        """
        return self._root

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its task.
        """
        return self._tools

    def new_workspace(self) -> Dir:
        """Creates a new, empty workspace without conditionals. Two
        workspaces created by this will never have the same name,
        so no need to worry whether the workspace has something inside or not.

        :return: Path to the created workspace.
        """
        workspace = self.root.cd(path=self.tools.folders.new_name())
        workspace.mkdir(recursive=True)

        LOG.debug("Created new workspace at: '%s'.", workspace)

        return workspace
