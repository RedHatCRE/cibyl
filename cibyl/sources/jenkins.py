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

import json
import logging
import re
from functools import partial

import requests

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic, custom_error=JenkinsError)


# pylint: disable=no-member
class Jenkins(Source):
    """A class representation of Jenkins client."""

    jobs_query = "?tree=jobs[name,url]"
    jobs_builds_query = "?tree=allBuilds[number,result]"

    # pylint: disable=too-many-arguments
    def __init__(self, url: str, username: str = None, token: str = None,
                 cert: str = None, name: str = "jenkins",
                 driver: str = "jenkins", priority: int = 0):
        """
            Create a client to talk to a jenkins instance.

            :param url: Jenkins instance address
            :type url: str
            :param username: Jenkins username
            :type username: str
            :param token: Jenkins access token
            :type token: str
            :param url: Jenkins instance address
            :type url: str
            :param cert: Path to a file with SSL certificates
            :type cert: str
        """
        super().__init__(name=name, url=url, driver=driver, priority=priority)
        self.username = username
        self.token = token
        self.cert = cert

    @safe_request
    def send_request(self, query, timeout=None, item=""):
        """
            Send a request to the jenkins instance and parse its json response.

            :param query: Part of the API request that specifies which data to
            request
            :type query: str
            :param timeout: How many seconds to wait for the server to send
            data before giving up
            :type timetout: float
            :param item: item to get information about
            :type item: str
            :returns: Information from the jenkins instance
            :rtype: dict
        """

        response = requests.get(f"{self.url}/{item}/api/json{query}",
                                verify=self.cert, timeout=timeout)
        response.raise_for_status()
        return json.loads(response.text)

    def get_jobs(self, **kwargs):
        """
            Get jobs from jenkins server.

            :returns: container of Job objects queried from jenkins server
            :rtype: :class:`AttributeDictValue`
        """
        jobs_arg = kwargs.get('jobs')
        pattern = None
        if jobs_arg:
            pattern = re.compile("|".join(jobs_arg.value))

        jobs_found = self.send_request(self.jobs_query)["jobs"]
        jobs_filtered = jobs_found
        if pattern:
            jobs_filtered = [job for job in jobs_found if re.search(pattern,
                                                                    job['name']
                                                                    )]
        job_objects = {}
        for job in jobs_filtered:
            if "job" not in job["_class"]:
                # jenkins may return folders as job objects
                continue
            name = job.get('name')
            job_objects[name] = Job(name=name, url=job.get('url'))

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def get_builds(self, **kwargs):
        """
            Get builds from jenkins server.

            :returns: container of jobs with build information from
            jenkins server
            :rtype: :class:`AttributeDictValue`
        """

        jobs_found = self.get_jobs(**kwargs)
        for job_name, job in jobs_found.items():
            builds_info = self.send_request(item=f"job/{job_name}",
                                            query=self.jobs_builds_query)
            if builds_info:
                for build in builds_info["allBuilds"]:
                    job.add_build(Build(str(build["number"]), build["result"]))

        return jobs_found
