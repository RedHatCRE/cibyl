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
from typing import Dict, List, Pattern

import requests
import urllib3

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, safe_request_generic

LOG = logging.getLogger(__name__)


safe_request = partial(safe_request_generic, custom_error=JenkinsError)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def satisfy_regex_match(model: Dict[str, str], pattern: Pattern,
                        field_to_check: str):
    """Check whether model (job or build) should be included according to
    the user input.
    The model should be added if the information provided field_to_check
    (the model name or url for example) is matches the regex pattern.

    :param model: model information obtained from jenkins
    :type model: str
    :param pattern: regex patter that the model name should match
    :type pattern: :class:`re.Pattern`
    :param field_to_check: model field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    return re.search(pattern, model[field_to_check]) is not None


def satisfy_exact_match(model: Dict[str, str], user_input: Argument,
                        field_to_check: str):
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is present in the user_input values.

    :param model: model information obtained from jenkins
    :type model: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    return model[field_to_check] in user_input.value


def satisfy_case_insensitive_match(model: Dict[str, str], user_input: Argument,
                                   field_to_check: str):
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is an exact case-insensitive match to
    the information in the user_input values.

    :param model: model information obtained from jenkins
    :type model: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    lowercase_input = [status.lower() for status in user_input.value]
    return model[field_to_check].lower() in lowercase_input


def filter_jobs(jobs_found: List[Dict], **kwargs):
    """Filter the result from the Jenkins API according to user input"""
    checks_to_apply = []

    jobs_arg = kwargs.get('jobs')
    if jobs_arg:
        pattern = re.compile("|".join(jobs_arg.value))
        checks_to_apply.append(partial(satisfy_regex_match, pattern=pattern,
                                       field_to_check="name"))

    job_names = kwargs.get('job_name')
    if job_names:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=job_names,
                                       field_to_check="name"))

    job_urls = kwargs.get('job_url')
    if job_urls:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=job_urls,
                                       field_to_check="url"))

    jobs_filtered = []
    for job in jobs_found:
        if "job" not in job["_class"]:
            # jenkins may return folders as job objects
            continue

        is_valid_job = True
        # we build the list of checks to apply dynamically depending on the
        # user input, to avoid repeating the same checks for every job
        for check in checks_to_apply:
            if not check(model=job):
                is_valid_job = False
                break

        if is_valid_job:
            jobs_filtered.append(job)

    return jobs_filtered


def filter_builds(builds_found: List[Dict], **kwargs):
    """Filter the result from the Jenkins API according to user input"""
    checks_to_apply = []

    builds_arg = kwargs.get('builds')
    if builds_arg and builds_arg.value:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=builds_arg,
                                       field_to_check="number"))

    build_ids = kwargs.get('build_id')
    if build_ids:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=build_ids,
                                       field_to_check="number"))

    build_status = kwargs.get('build_status')
    if build_status:
        checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=build_status,
                                       field_to_check="result"))

    builds_filtered = []
    for build in builds_found:
        is_valid_build = True
        # ensure that the build number is passed as a string, Jenkins usually
        # sends it as an int
        build["number"] = str(build["number"])
        # we build the list of checks to apply dynamically depending on the
        # user input, to avoid repeating the same checks for every build
        for check in checks_to_apply:
            if not check(model=build):
                is_valid_build = False
                break

        if is_valid_build:
            builds_filtered.append(build)

    return builds_filtered


# pylint: disable=no-member
class Jenkins(Source):
    """A class representation of Jenkins client."""

    jobs_query = "?tree=jobs[name,url]"
    jobs_builds_query = {0: "?tree=allBuilds[number,result]",
                         1: "?tree=allBuilds[number,result,duration]",
                         2: "?tree=allBuilds[number,result,duration]",
                         3: "?tree=allBuilds[number,result,duration]"}
    jobs_last_build_query = "?tree=jobs[name,url,lastBuild[number,result]]"

    # pylint: disable=too-many-arguments
    def __init__(self, url: str, username: str = None, token: str = None,
                 cert: str = None, name: str = "jenkins",
                 driver: str = "jenkins", enabled: bool = True,
                 priority: int = 0):
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
        super().__init__(name=name, url=url, driver=driver,
                         enabled=enabled, priority=priority)
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
            :type timeout: float
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
        jobs_found = self.send_request(self.jobs_query)["jobs"]
        jobs_filtered = filter_jobs(jobs_found, **kwargs)

        job_objects = {}
        for job in jobs_filtered:
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
        if kwargs.get('verbosity', 0) > 0 and len(jobs_found) > 80:
            LOG.warning("This might take a couple of minutes...\
try reducing verbosity for quicker query")
        LOG.debug("Requesting builds for %d jobs", len(jobs_found))
        for job_name, job in jobs_found.items():
            builds_info = self.send_request(item=f"job/{job_name}",
                                            query=self.jobs_builds_query.get(
                                                kwargs.get('verbosity'), 0))
            if builds_info:
                LOG.debug("Got %d builds for job %s",
                          len(builds_info["allBuilds"]), job_name)
                for build in builds_info["allBuilds"]:
                    job.add_build(Build(str(build["number"]), build["result"],
                                        duration=build.get('duration')))
                builds_to_add = filter_builds(builds_info["allBuilds"],
                                              **kwargs)
                for build in builds_to_add:
                    job.add_build(Build(build["number"], build["result"]))

        return jobs_found

    def get_last_build(self, **kwargs):
        """
            Get last build for jobs from jenkins server.

            :returns: container of jobs with build information from
            jenkins server
            :rtype: :class:`AttributeDictValue`
        """

        jobs_found = self.send_request(self.jobs_last_build_query)["jobs"]
        jobs_filtered = filter_jobs(jobs_found, **kwargs)

        job_objects = {}
        for job in jobs_filtered:
            name = job.get('name')

            job_object = Job(name=name, url=job.get('url'))
            if job["lastBuild"]:
                builds_to_add = filter_builds([job["lastBuild"]],
                                              **kwargs)
                for build in builds_to_add:
                    build_obj = Build(build["number"], build["result"])
                    job_object.add_build(build_obj)
            job_objects[name] = job_object

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)
