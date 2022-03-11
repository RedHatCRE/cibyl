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
from functools import partial

import jenkins
import requests

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings()


safe_request = partial(safe_request_generic, custom_error=JenkinsError)


# pylint: disable=no-member
class Jenkins(Source):
    """A class representation of Jenkins client."""

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
        self.client = jenkins.Jenkins(url, username=username, password=token)
        self.client._session.verify = cert

    @safe_request
    def get_jobs(self, **kwargs):
        """
            Get all jobs from jenkins server.

            :returns: List of Job objects from jenkins server
            :rtype: list
        """
        jobs_arg = kwargs.get('jobs')
        if not jobs_arg:
            jobs_arg = [""]
        jobs_result = {}

        # default case, where user wants all jobs
        jobs_found = []
        for job in jobs_arg:
            jobs_found = self.client.run_script(
                f"""
                import groovy.json.JsonBuilder;
                items = Jenkins.instance.getAllItems().findAll(
                    {{ item -> item.getFullName().contains("{job}") }});
                def json = new JsonBuilder();
                json {{jobs items.collect {{[name: it.name, url: it.url]}}}};
                println json.toString();
                """)
            jobs_found_json = json.loads(jobs_found)['jobs']
            jobs_result['jobs'] = {
                job.get('name'): Job(name=job.get('name'), url=job.get('url'))
                for job in jobs_found_json}

        return jobs_result

    def get_builds(self, **kwargs):
        """
            Get builds from jenkins server.

            :returns: List of jobs with build information from jenkins server
            :rtype: list
        """

        jobs_found = self.get_jobs(**kwargs)
        for job in jobs_found:
            builds_info = self.client.get_info(item="job/"+job.name.value,
                                               query=self.jobs_builds_query)
            if builds_info:
                for build in builds_info["allBuilds"]:
                    job.add_build(Build(str(build["number"]), build["result"]))

        return jobs_found


class JenkinsOSP(Jenkins):
    """A class representation of OSP Jenkins client."""

    # pylint: disable=useless-super-delegation
    def __init__(self, url: str, username: str, token: str, cert: str = None):
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
        super().__init__(url, username, token, cert)
