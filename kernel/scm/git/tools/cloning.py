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
from dataclasses import dataclass, field
from typing import Optional

from kernel.scm.git.apis.cli import Git, GitError, Repository
from kernel.scm.git.apis.cli.gitpython import GitPython
from kernel.scm.tools.fs import WorkspaceFactory
from kernel.tools.cache import Cache, RTCache
from kernel.tools.fs import Dir
from kernel.tools.urls import URL

LOG = logging.getLogger(__name__)


class RepositoryFactory:
    """Utility used to clone and keep track of git repositories.

    Unlike other factories, this one is stateful. This means that it holds a
    cache of what it has created before. For its case, the factory will
    take care of cloning git repositories and holding into memory where it
    did so. If another request to clone the same repository arrives,
    then the help copy is returned instead.

    This factory satisfies a very particular case then, where storage space
    and time are prioritized over data integrity. Bear in mind that two
    references returned by this factory may point to the same repository,
    which will make the changes from one affect the other. However, in the
    case that the repository is meant for just reading, and no modification
    is performed over it, then it is useful to go back to a copy of the
    repository without having to download it again once more.
    """

    @dataclass
    class Tools:
        git: Git = field(
            default_factory=lambda *_: GitPython()
        )
        workspaces: WorkspaceFactory = field(
            default_factory=lambda *_: WorkspaceFactory()
        )

    def __init__(
        self,
        memory: Optional[Cache[URL, Dir]] = None,
        tools: Optional[Tools] = None
    ):
        if memory is None:
            memory = RTCache[URL, Dir](
                loader=lambda *_: self.tools.workspaces.new_workspace()
            )

        if tools is None:
            tools = RepositoryFactory.Tools()

        self._memory = memory
        self._tools = tools

    @property
    def memory(self) -> Cache[URL, Dir]:
        return self._memory

    @property
    def tools(self) -> Tools:
        return self._tools

    def from_remote(self, url: URL) -> Repository:
        workspace = self.memory.get(url)

        # Check if the workspace is brand new...
        if workspace.is_empty():
            # Download the repository into it then
            return self.tools.git.clone(url, workspace)

        # There is something on the repository already...
        try:
            # See if it is a git repository
            return self.tools.git.open(workspace)
        except GitError:
            LOG.warning(
                "Unable to open repository at: '%s'. "
                "Cloning again into a new workspace...",
                workspace
            )

            # Forget about the workspace and try again
            self.memory.delete(url)
            self.from_remote(url)
