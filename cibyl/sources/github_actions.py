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
from functools import partial

import urllib3
from github import Github

from cibyl.exceptions.github_actions import GithubActionsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.github_actions.workflow import Workflow
from cibyl.sources.server import ServerSource
from cibyl.sources.source import safe_request_generic, speed_index

LOG = logging.getLogger(__name__)

safe_request = partial(safe_request_generic, custom_error=GithubActionsError)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# pylint: disable=no-member
class GithubActions(ServerSource):
    """A class representation of GitHub Actions client."""

    # pylint: disable=too-many-arguments
    def __init__(self, repos: list, token: str = None,
                 name: str = "github_actions",
                 driver: str = "github_actions", enabled: bool = True,
                 priority: int = 0):
        """
            Create a client for GitHub Actions

            :param token: Jenkins access token
            :type token: str
        """
        super().__init__(name=name, driver=driver,
                         enabled=enabled, priority=priority)
        self.repos = repos
        self.token = token
        self.github = Github(token, verify=False)

    @speed_index({'base': 0})
    def get_workflows(self, **kwargs):
        workflows = {}
        for repo in self.repos:
            github_repo = self.github.get_repo(repo['name'])
            repo_workflows = github_repo.get_workflows()
            for workflow in repo_workflows:
                workflows[workflow.name] = Workflow(
                    name=workflow.name, url=workflow.url)
        return AttributeDictValue("workflows", attr_type=Workflow,
                                  value=workflows)
