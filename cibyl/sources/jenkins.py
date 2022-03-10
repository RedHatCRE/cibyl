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

import jenkins

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic, custom_error=JenkinsError)


# pylint: disable=no-member
class Jenkins(Source):
    """A class representation of Jenkins client."""

    jobs_query = "?tree=jobs[name,url]"
    jobs_builds_query = "?tree=jobs[name,url,builds[number,result]]"

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
    def get_jobs(self, get_builds: bool = False, **kwargs):
        """
            Get all jobs from jenkins server.

            :param get_builds: Whether to get info about the jobs' builds
            :type get_builds: bool

            :returns: All jobs from jenkins server, as dictionaries of _class,
            name, fullname, url, color
            :rtype: list
        """
        if get_builds:
            return self.client.get_info(query=self.jobs_builds_query)["jobs"]
        jobs_arg = kwargs.get('jobs')
        if jobs_arg:
            for job in jobs_arg.value:
                return self.client.get_job_info_regex(pattern=job)

        return self.client.get_info(query=self.jobs_query)["jobs"]

    # pylint: disable=no-self-use
    def populate_jobs(self, system, jobs: list[dict]):
        """
            Create Job models using jenkins jobs information.

            :param system: System model to input the jobs to
            :type system: :class:`cibyl.models.ci.system.System`
            :param jobs: Jobs received from jenkins server
            :type jobs: list
        """
        for job in jobs:
            if "job" not in job["_class"]:
                # jenkins may return folders as job objects
                continue
            job_name = job.get('name')
            builds_info = job.get('builds')
            builds = None
            if builds_info:
                builds = [Build(str(build["number"]), build["result"])
                          for build in builds_info]

            system.jobs.append(Job(name=job_name, url=job.get('url'),
                                   builds=builds))

    # pylint: disable=inconsistent-return-statements
    def query(self, system, args):
        LOG.debug("querying system %s using source: %s",
                  system.name.value, self.__name__)

        if args.get('jobs'):
            jobs = self.get_jobs(args.get('builds', False))
            self.populate_jobs(system, jobs)

        if all(argument.populated for argument in args):
            return system


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
