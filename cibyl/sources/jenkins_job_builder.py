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
from cibyl.sources.git import GitSource
from cibyl.sources.source import safe_request_generic, speed_index

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic,
                       custom_error=JenkinsJobBuilderError)


# pylint: disable=no-member
class JenkinsJobBuilder(GitSource):
    """A class representation of a JenkinsJobBuilder repo."""

    # pylint: disable=too-many-arguments
    def __init__(self, repos: dict = None,
                 enabled: bool = True, priority: int = 0,
                 name: str = "jenkins_job_builder",
                 driver: str = "jenkins_job_builder"):
        """Create a client to talk to a jenkins job definitions instance.

        :param repos: A dictionary of repositories to clone
        :type repos: dict
        """
        super().__init__(name=name, repos=repos, driver=driver,
                         enabled=enabled, priority=priority)

    def _generate_xml(self):
        """Use tox to generate jenkins job xml files."""
        for repo in self.repos:
            subprocess.run(["tox",  "-e", "jobs"], check=True,
                           cwd=repo.get('dest'))

    @speed_index({'base': 1})
    def get_jobs(self, **kwargs):
        """Get all jobs from jenkins server.

        :returns: All jobs from jenkins server, as dictionaries of _class,
        name, fullname, url, color
        :rtype: list
        """
        all_jobs = {}
        for repo in self.repos:
            all_jobs.update(self.get_jobs_from_repo(repo, **kwargs))
        return AttributeDictValue("jobs", attr_type=Job, value=all_jobs)

    def get_jobs_from_repo(self, repo, **kwargs):
        """Get all jobs from a given repo

        :param repo: repo information like path and url
        :type repo: dict
        :returns: All jobs from the given repository
        :rtype: dict
        """
        self._generate_xml()
        jobs_available = {}
        jobs_arg = kwargs.get('jobs')
        pattern = None
        if jobs_arg:
            pattern = re.compile("|".join(jobs_arg.value))

        jobs_found = []
        for path in Path(os.path.join(repo.get('dest'),
                                      "out-xml")).rglob("*.xml"):
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
        return jobs_available
