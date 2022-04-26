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
    def __init__(self, repos: dict = None,
                 enabled: bool = True, priority: int = 0,
                 name: str = "git", driver: str = None):
        """Create a client to talk to a jenkins job definitions instance.

        :param repos: A dictionary of repositories to clone
        :type repos: dict
        """
        super().__init__(name, driver=driver,
                         enabled=enabled, priority=priority)
        self.repos = repos

    def setup(self):
        """Clone the repositories specified by the 'repos' argument/field."""
        super().setup()
        for repo in self.repos:
            if repo.get('dest') is None and repo.get('url') is None:
                message = f"Source {self.name} needs a url or \
a destination path."
                raise GitError(message)
            if repo.get('dest') is None:
                repo_name = os.path.split(repo.get('url'))[-1]
                project_name = os.path.splitext(repo_name)[0]
                repo['dest'] = os.path.join(os.path.expanduser('~'), '.cibyl',
                                            project_name)
                os.makedirs(repo.get('dest'), exist_ok=True)
        self.ensure_repos_present()

    def ensure_repos_present(self):
        """Ensure that the repository with job definitions is present."""
        for repo in self.repos:
            if repo.get('cloned'):
                continue
            if not os.path.exists(os.path.join(repo.get('dest'), ".git")):
                LOG.debug("cloning repository %s to %s", repo.get('url'),
                          repo.get('dest'))
                self.get_repo()
            else:
                LOG.debug("Repository %s found in %s, pulling latest changes",
                          repo.get('url'), repo.get('dest'))
                self.pull_latest_changes(repo.get('dest'))
                repo['cloned'] = True

    @safe_request
    def pull_latest_changes(self, repo_path):
        """Ensure that the repo is up to date."""
        repo = Repo(repo_path)
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
