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
import re
import subprocess
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path

from cibyl.exceptions.jenkins_job_builder import JenkinsJobBuilderError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic, speed_index

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic,
                       custom_error=JenkinsJobBuilderError)


# pylint: disable=no-member
class JenkinsJobBuilder(Source):
    """A class representation of a JenkinsJobBuilder repo."""

    # pylint: disable=too-many-arguments
    def __init__(self, url: str = None, dest: str = None, branch: str = None,
                 enabled: bool = True, priority: int = 0,
                 name: str = "jenkins_job_builder",
                 driver: str = "jenkins_job_builder"):
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
            raise JenkinsJobBuilderError(message)

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
        branch = []
        if self.branch:
            subprocess.run(["git", "checkout", self.branch], check=True,
                           cwd=self.dest)
            branch.append(self.branch)

        subprocess.run(["git", "pull", "origin"]+branch, check=True,
                       cwd=self.dest)

    @safe_request
    def get_repo(self):
        """Download git repository for job definitions."""
        branch_options = []
        if self.branch is not None:
            branch_options = ["-b", self.branch]
        subprocess.run(["git", "clone", self.url, self.dest]+branch_options,
                       check=True)

    def _generate_xml(self):
        """Use tox to generate jenkins job xml files."""
        subprocess.run(["tox",  "-e", "jobs"], check=True, cwd=self.dest)

    @speed_index({'jobs': 1})
    def get_jobs(self, **kwargs):
        """Get all jobs from jenkins server.

        :returns: All jobs from jenkins server, as dictionaries of _class,
        name, fullname, url, color
        :rtype: list
        """
        self.ensure_repo_present()
        self._generate_xml()
        jobs_available = {}
        jobs_arg = kwargs.get('jobs')
        pattern = None
        if jobs_arg:
            pattern = re.compile("|".join(jobs_arg.value))

        jobs_found = []
        for path in Path(os.path.join(self.dest, "out-xml")).rglob("*.xml"):
            file_content = ET.parse(path).getroot()
            file_type = file_content.tag
            if "folder" in file_type:
                # if the xml file contains the word folder in the top-level
                # attribute, then it's probably not a job
                continue
            # for now we store the job name as the only information, later we
            # will need to see which additional information to pull from the
            # job definition
            jobs_found.append(path.parent.name)
        jobs_filtered = jobs_found
        if pattern:
            # filter the found jobs and keep only those specified in the user
            # input
            jobs_filtered = [job for job in jobs_found if re.search(pattern,
                                                                    job
                                                                    )]
        for job in jobs_filtered:
            jobs_available[job] = Job(name=job)

        return AttributeDictValue("jobs", attr_type=Job, value=jobs_available)
