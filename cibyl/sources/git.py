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
import os
from functools import partial

from git import Repo

from cibyl.exceptions.git import GitError
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)

safe_request = partial(safe_request_generic,
                       custom_error=GitError)


class GitSource(Source):
    """A class representation of a Git-based source."""

    # pylint: disable=too-many-arguments
    def __init__(self, url: str = None, dest: str = None, branch: str = None,
                 enabled: bool = True, priority: int = 0,
                 name: str = "git", driver: str = None):
        """Create a client to talk to a jenkins job definitions instance.

        :param url: Job definitions address
        :type url: str
        :param dest: Path to the repository, or where to store it
        :type dest: str
        :param branch: Branch to checkout
        :type branch: str
        """
        super().__init__(name, url=url, driver=driver,
                         enabled=enabled, priority=priority)
        self.dest = dest
        self.branch = branch
        self.cloned = False
        if self.dest is None and self.url is None:
            message = f"Source {self.name} needs a url or a destination path."
            raise GitError(message)

        if dest is None:
            repo_name = os.path.split(self.url)[-1]
            project_name = os.path.splitext(repo_name)[0]
            self.dest = os.path.join(os.path.expanduser('~'), '.cibyl',
                                     project_name)
            os.makedirs(self.dest, exist_ok=True)

    def ensure_repo_present(self):
        """Ensure that the repository with job definitions is present."""
        if self.cloned:
            return
        self.cloned = True
        if not os.path.exists(os.path.join(self.dest, ".git")):
            LOG.debug("cloning repository %s to %s", self.url, self.dest)
            self.get_repo()
        else:
            LOG.debug("Repository %s found in %s, pulling latest changes",
                      self.url, self.dest)
            self.pull_latest_changes()

    @safe_request
    def pull_latest_changes(self):
        """Ensure that the repo is up to date."""
        repo = Repo(self.dest)
        repo_remote = repo.remotes.origin
        repo_remote.pull()

    @safe_request
    def get_repo(self):
        """Download git repository for job definitions."""
        branch_options = []
        if self.branch is not None:
            branch_options = ["-b", self.branch]
        Repo.clone_from(self.url, to_path=self.dest,
                        multi_options=branch_options)
