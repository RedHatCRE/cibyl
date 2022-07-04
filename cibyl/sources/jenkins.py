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
from typing import Callable, Dict, List
from urllib.parse import urlparse

import requests
import urllib3

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.stage import Stage
from cibyl.models.ci.base.test import Test
from cibyl.sources.server import ServerSource
from cibyl.sources.source import safe_request_generic, speed_index
from cibyl.utils.filtering import (apply_filters,
                                   satisfy_case_insensitive_match,
                                   satisfy_exact_match, satisfy_range_match,
                                   satisfy_regex_match)
from cibyl.utils.models import has_builds_job, has_tests_job

LOG = logging.getLogger(__name__)

safe_request = partial(safe_request_generic, custom_error=JenkinsError)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_job_info_regex(job_name, pattern, group_index=0, default=""):
    """Extract information from a jenkins job name using regex, if not present,
    set to a default value.

    :param job: Jenkins Job representation as a dictionary
    :type job: dict
    :returns: The substring of the job name matchin pattern if present,
    '' otherwise
    :rtype: str
    """
    match_job = pattern.search(job_name)
    if match_job:
        return match_job.group(group_index)
    return default


def is_job(job):
    """Check if a given job representation corresponds to a job and not
    a folder or a view.

    :param job: Jenkins Job representation as a dictionary
    :type job: dict
    :returns: Whether the job representation actually corresponds to a job
    :rtype: bool
    """
    job_class = job["_class"].lower()
    return not ("view" in job_class or "folder" in job_class or "multibranch"
                in job_class)


def filter_jobs(jobs_found: List[Dict], **kwargs):
    """Filter the result from the Jenkins API according to user input"""
    checks_to_apply = [is_job]

    jobs_arg = kwargs.get('jobs')
    if jobs_arg and jobs_arg.value:
        pattern = re.compile("|".join(jobs_arg.value))
        checks_to_apply.append(partial(satisfy_regex_match, pattern=pattern,
                                       field_to_check="name"))

    jobs_scope_arg = kwargs.get('jobs_scope')
    if jobs_scope_arg:
        pattern = re.compile(jobs_scope_arg)
        checks_to_apply.append(partial(satisfy_regex_match, pattern=pattern,
                                       field_to_check="name"))

    spec_jobs_name_arg = kwargs.get('spec')
    if spec_jobs_name_arg and spec_jobs_name_arg.value:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=spec_jobs_name_arg,
                                       field_to_check="name"))

    return apply_filters(jobs_found, *checks_to_apply)


def get_build_filters(**kwargs: Argument) -> List[Callable]:
    """Get a list of functions that should be used to filter the builds,
    according to user input."""
    checks_to_apply = []
    builds_arg = kwargs.get('builds')
    if builds_arg and builds_arg.value:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=builds_arg,
                                       field_to_check="number"))

    build_status = kwargs.get('build_status')
    if build_status and build_status.value:
        checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=build_status,
                                       field_to_check="result"))
    return checks_to_apply


def get_test_filters(**kwargs: Argument) -> List[Callable]:
    """Get a list of functions that should be used to filter the tests,
    according to user input."""
    checks_to_apply = []
    tests_arg = kwargs.get('tests')
    if tests_arg and tests_arg.value:
        pattern = re.compile("|".join(tests_arg.value))
        checks_to_apply.append(partial(satisfy_regex_match,
                                       pattern=pattern,
                                       field_to_check="name"))

    tests_results = kwargs.get('test_result')
    if tests_results and tests_results.value:
        checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=tests_results,
                                       field_to_check="status"))

    test_durations = kwargs.get('test_duration')
    if test_durations and test_durations.value:
        checks_to_apply.append(partial(satisfy_range_match,
                                       user_input=test_durations,
                                       field_to_check="duration"))
    return checks_to_apply


def filter_builds(builds_found: List[Dict],
                  checks_to_apply: List[Callable]) -> List[Dict]:

    """Filter the result from the Jenkins API according to user input
    :param builds_found: Collection of builds to filter
    :param: checks_to_apply: List of function that the builds should satisfy
    :returns: The builds that satisfy all the conditions included in the checks
    functions
    """

    for build in builds_found:
        # ensure that the build number is passed as a string, Jenkins usually
        # sends it as an int
        build["number"] = str(build["number"])

    return apply_filters(builds_found, *checks_to_apply)


def is_test(test: dict) -> bool:
    """Check if a given test representation corresponds to a test and not
    to some container returned by Jenkins.

    :param test: Jenkins Job representation as a dictionary
    :returns: Whether the test representation actually corresponds to a test
    """
    # If the test does not have a className, then it is a container
    return bool(test['className'])


def filter_tests(tests_found: List[Dict],
                 checks_to_apply: List[Callable]) -> List[Dict]:
    """Filter the tests obtained from the Jenkins API according to
    user input.
    :param tests_found: Collection of tests to filter
    :param: checks_to_apply: List of function that the tests should satisfy
    :returns: The tests that satisfy all the conditions included in the checks
    functions
    """
    return apply_filters(tests_found, is_test, *checks_to_apply)


# pylint: disable=no-member
class Jenkins(ServerSource):
    """A class representation of Jenkins client."""

    jobs_query = "?tree=jobs[name,url]"
    jobs_builds_query = {0: "?tree=allBuilds[number,result]",
                         1: "?tree=allBuilds[number,result,duration]",
                         2: "?tree=allBuilds[number,result,duration]",
                         3: "?tree=allBuilds[number,result,duration]"}
    jobs_last_build_query = "?tree=jobs[name,url,lastBuild[number,result]]"
    jobs_query_for_deployment = \
        "?tree=jobs[name,url,lastCompletedBuild[number,result,description]]"

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
    def send_request(self, query, timeout=None, item="",
                     api_entrypoint="/api/json", raw_response=False,
                     url=None):
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
            :param api_entrypoint: API entrypoint to use, by default use
            api/json
            :type api_entrypoint: str
            :param raw_response: Whether to return the text of the response
            without any processing
            :type raw_response: bool
            :param url: url to send the request to
            :type url: str

            :returns: Information from the jenkins instance
            :rtype: dict
        """

        def generate_query_url():
            base = urlparse(self.url)

            # Add protocol
            url = f'{base.scheme}://'

            # Add user and pass
            if self.username:
                url += f'{self.username}'

                if self.token:
                    url += f':{self.token}'

                url += '@'

            # Add host name
            url += f'{base.netloc}'

            # Add path
            if item:
                url += f'/{item}'

            url += f'{api_entrypoint}{query}'

            return url

        if url is None:
            url = generate_query_url()
        response = requests.get(
            url, verify=self.cert, timeout=timeout
        )

        response.raise_for_status()
        if raw_response:
            return response.text

        return json.loads(response.text)

    @speed_index({'base': 2})
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

    def _get_stages(self, job_name, build_number):
        """
            Get CI stages executed in a build from jenkins server.

            :param job_name: Jenkins job name to query the information for
            :type job_name: str
            :param build_number: Jenkins build number to query the
            information for
            :type build_number: str

            :returns: container with stages information from
            jenkins server
            :rtype: :class:`AttributeListValue`
        """
        query = f"/{job_name}/{build_number}/wfapi/describe"
        stages = self.send_request(query=query, api_entrypoint="", item="job")
        if not stages["stages"]:
            return None
        stages_collection = AttributeListValue("stages", attr_type=Stage)
        for stage in stages["stages"]:
            stages_collection.append(
                    Stage(stage["name"], stage.get("status"),
                          duration=stage.get("durationMillis")))
        return stages_collection

    @speed_index({'base': 1, 'last_build': 1})
    def get_builds(self, **kwargs):
        """
            Get builds from jenkins server.

            :returns: container of jobs with build information from
            jenkins server
            :rtype: :class:`AttributeDictValue`
        """

        if 'last_build' in kwargs:
            return self.get_last_build(**kwargs)
        jobs_found = self.get_jobs(**kwargs)
        build_filters = get_build_filters(**kwargs)
        filtering_builds = bool(build_filters)
        jobs_with_builds = {}
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
                builds_to_add = filter_builds(builds_info["allBuilds"],
                                              build_filters)
                for build in builds_to_add:
                    build_stages = None
                    if "stages" in kwargs:
                        build_stages = self._get_stages(job_name,
                                                        build["number"])
                    build_object = Build(build["number"], build["result"],
                                         duration=build.get('duration'),
                                         stages=build_stages)
                    job.add_build(build_object)

            has_builds = has_builds_job(job)
            if (filtering_builds and has_builds) or not filtering_builds:
                jobs_with_builds[job_name] = job

        jobs_found.value = jobs_with_builds
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
        build_filters = get_build_filters(**kwargs)
        filtering_builds = bool(build_filters)

        job_objects = {}
        for job in jobs_filtered:
            name = job.get('name')

            job_object = Job(name=name, url=job.get('url'))
            if job["lastBuild"]:
                builds_to_add = filter_builds([job["lastBuild"]],
                                              build_filters)
                for build in builds_to_add:
                    build_stages = None
                    if "stages" in kwargs:
                        build_stages = self._get_stages(name,
                                                        build["number"])
                    build_obj = Build(build["number"], build["result"],
                                      duration=build.get('duration'),
                                      stages=build_stages)
                    job_object.add_build(build_obj)
            has_builds = has_builds_job(job_object)
            if (filtering_builds and has_builds) or not filtering_builds:
                job_objects[name] = job_object

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    @speed_index({'base': 2})
    def get_tests(self, **kwargs):
        """
            Get tests for a Jenkins job.

            :returns: container of jobs with the selected build(s)
             and their tests
            :rtype: :class:`AttributeDictValue`
        """

        self.check_builds_for_test(**kwargs)
        checks_user_input = get_test_filters(**kwargs)
        filtering_tests = bool(checks_user_input)

        jobs_found = self.get_builds(**kwargs)
        final_jobs = {}

        for job_name, job in jobs_found.items():
            for build_id, build in job.builds.items():
                if build.status.value == 'FAILURE':
                    LOG.warning("Build %s for job %s failed. No tests to "
                                "fetch", build_id, job_name)
                    continue

                # Get the tests for this build
                try:
                    tests_found = self.send_request(
                        item=f"job/{job_name}/{build_id}/testReport",
                        query='')
                except JenkinsError as jerr:
                    if '404' in str(jerr):
                        LOG.warning("No tests found for build %s for job %s",
                                    build_id, job_name)
                        continue
                    else:
                        raise jerr

                test_suites = []
                if 'suites' in tests_found:
                    test_suites = tests_found['suites']

                # Some jobs have the test report in a child container
                if 'childReports' in tests_found:
                    for child_report in tests_found['childReports']:
                        for suit in child_report['result']['suites']:
                            test_suites.append(suit)

                if not test_suites:
                    LOG.warning("No test suites found for job %s", job_name)
                    continue

                for suit_id, suit in enumerate(test_suites):
                    if 'cases' not in suit:
                        LOG.warning("No 'cases' found in test suit %d for job"
                                    " %s", suit_id, job_name)
                        continue

                    tests_filtered = filter_tests(suit['cases'],
                                                  checks_user_input)
                    for test in tests_filtered:

                        # Duration comes in seconds (float)
                        duration_in_ms = test.get('duration')*1000
                        build.add_test(
                            Test(name=test.get('name'),
                                 class_name=test.get('className'),
                                 result=test.get('status'),
                                 duration=duration_in_ms))
            has_tests = has_tests_job(job)
            if (filtering_tests and has_tests) or not filtering_tests:
                final_jobs[job_name] = job

        return AttributeDictValue("jobs", attr_type=Job, value=final_jobs)
