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
from tempfile import TemporaryDirectory

from cibyl.exceptions.jenkins_job_builder import JenkinsJobBuilderError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic,
                       custom_error=JenkinsJobBuilderError)


# pylint: disable=no-member
class JenkinsJobBuilder(Source):
    """A class representation of a JenkinsJobBuilder repo."""

    # pylint: disable=too-many-arguments
    def __init__(self, url: str = None, dest: str = None, branch: str = None,
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
        super().__init__(name, url=url, driver=driver)
        self.dest = dest
        self.branch = branch
        if dest is None:
            # store the TemporaryDirectory directory, so that the contents live
            # until the instance of self is destroyed
            # pylint: disable=consider-using-with
            self.tmp_folder = TemporaryDirectory()
            self.dest = self.tmp_folder.name

        if not os.path.exists(os.path.join(self.dest, ".git")):
            LOG.debug("cloning repository to %s", self.dest)
            self.get_repo()
        else:
            LOG.debug("repository already present in %s", self.dest)

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

    def get_jobs(self, **kwargs):
        """Get all jobs from jenkins server.

        :returns: All jobs from jenkins server, as dictionaries of _class,
        name, fullname, url, color
        :rtype: list
        """
        self._generate_xml()
        jobs_available = {}
        jobs_arg = kwargs.get('jobs', ["*"])
        if jobs_arg == ["*"] or jobs_arg.value == ["*"]:
            # default case, where user wants all jobs
            pattern = re.compile(".*")
        else:
            pattern = re.compile(".*"+".*|.*".join(jobs_arg.value)+".*")

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
            # filter the found jobs and keep only those specified in the user
            # input
            if pattern.match(path.parent.name):
                jobs_available[path.parent.name] = Job(name=path.parent.name)

        return AttributeDictValue("jobs", attr_type=Job, value=jobs_available)
