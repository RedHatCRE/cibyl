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
from typing import Dict, List
from urllib.parse import urlparse

import requests
import urllib3

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.models.ci.test import Test
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.utils import translate_topology_string
from cibyl.sources.source import Source, safe_request_generic, speed_index
from cibyl.utils.filtering import (DEPLOYMENT_PATTERN, DVR_PATTERN_NAME,
                                   DVR_PATTERN_RUN, IP_PATTERN,
                                   NETWORK_BACKEND_PATTERN, OPTIONS,
                                   PROPERTY_PATTERN, RELEASE_PATTERN,
                                   RELEASE_RUN, RELEASE_VERSION,
                                   STORAGE_BACKEND_PATTERN, TLS_PATTERN_RUN,
                                   TOPOLOGY_PATTERN, apply_filters,
                                   filter_topology,
                                   satisfy_case_insensitive_match,
                                   satisfy_exact_match, satisfy_regex_match)

LOG = logging.getLogger(__name__)

safe_request = partial(safe_request_generic, custom_error=JenkinsError)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_job_info_regex(job_name, pattern, group_index=0, default=""):
    """Extract information from a jenkins job name using regex, if not present,
    set to a default value.

    :param job: Jenkins Job representation as a dictionary
    :type job: dict
    :returns: The ip version used for the job if present, 'unknown' otherwise
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
    if jobs_arg:
        pattern = re.compile("|".join(jobs_arg.value))
        checks_to_apply.append(partial(satisfy_regex_match, pattern=pattern,
                                       field_to_check="name"))

    job_urls = kwargs.get('job_url')
    if job_urls:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=job_urls,
                                       field_to_check="url"))

    return apply_filters(jobs_found, *checks_to_apply)


def filter_builds(builds_found: List[Dict], **kwargs):
    """Filter the result from the Jenkins API according to user input"""
    checks_to_apply = []

    builds_arg = kwargs.get('builds')
    if builds_arg and builds_arg.value:
        checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=builds_arg,
                                       field_to_check="number"))

    build_status = kwargs.get('build_status')
    if build_status:
        checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=build_status,
                                       field_to_check="result"))

    for build in builds_found:
        # ensure that the build number is passed as a string, Jenkins usually
        # sends it as an int
        build["number"] = str(build["number"])

    return apply_filters(builds_found, *checks_to_apply)


# pylint: disable=no-member
class Jenkins(Source):
    """A class representation of Jenkins client."""

    jobs_query = "?tree=jobs[name,url]"
    jobs_builds_query = {0: "?tree=allBuilds[number,result]",
                         1: "?tree=allBuilds[number,result,duration]",
                         2: "?tree=allBuilds[number,result,duration]",
                         3: "?tree=allBuilds[number,result,duration]"}
    jobs_last_build_query = "?tree=jobs[name,url,lastBuild[number,result]]"
    jobs_last_completed_build_query = \
        "?tree=jobs[name,url,lastCompletedBuild[number,result,duration]]"
    build_tests_query = "?tree=suites[cases[name,status,duration,className]]"

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
        self.deployment_attr = ["topology", "release",
                                "network_backend", "storage_backend",
                                "infra_type", "dvr", "ip_version",
                                "tls_everywhere"]

    @safe_request
    def send_request(self, query, timeout=None, item="",
                     api_entrypoint="/api/json", raw_response=False):
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

        response = requests.get(
            generate_query_url(), verify=self.cert, timeout=timeout
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

    @speed_index({'base': 1, 'last_build': 1})
    def get_builds(self, **kwargs):
        """
            Get builds from jenkins server.

            :returns: container of jobs with build information from
            jenkins server
            :rtype: :class:`AttributeDictValue`
        """

        if kwargs.get('last_build'):
            return self.get_last_build(**kwargs)
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
                builds_to_add = filter_builds(builds_info["allBuilds"],
                                              **kwargs)
                for build in builds_to_add:
                    job.add_build(Build(build["number"], build["result"],
                                        duration=build.get('duration')))

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
                    build_obj = Build(build["number"], build["result"],
                                      duration=build.get('duration'))
                    job_object.add_build(build_obj)
            job_objects[name] = job_object

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    @speed_index({'base': 2})
    def get_tests(self, **kwargs):
        """
            Get tests for a Jenkins job.

            :returns: container of jobs with the last completed build
            (if any) and the tests
            :rtype: :class:`AttributeDictValue`
        """

        # Get the jobs with the last completed build (default behavior)
        jobs_found = self.send_request(
            self.jobs_last_completed_build_query)["jobs"]
        jobs_filtered = filter_jobs(jobs_found, **kwargs)

        job_objects = {}

        for job in jobs_filtered:
            job_name = job.get('name')
            if job["lastCompletedBuild"] is None:
                LOG.warning("No completed builds found for job %s", job_name)
                continue

            job_object = Job(name=job_name, url=job.get('url'))
            job_objects[job_name] = job_object

            if kwargs.get('builds'):
                # For specific build ids we have to fetch them
                builds = self.send_request(item=f"job/{job_name}",
                                           query=self.jobs_builds_query.get(
                                               kwargs.get('verbosity'), 0))
                builds_to_add = filter_builds(builds["allBuilds"], **kwargs)
            else:
                builds_to_add = filter_builds([job["lastCompletedBuild"]],
                                              **kwargs)

            if not builds_to_add:
                LOG.warning("No builds found for job %s", job_name)
                continue

            for build in builds_to_add:
                build_object = Build(
                    build_id=build['number'],
                    status=build['result'])

                job_objects[job_name].add_build(build_object)

                if build['result'] == 'FAILURE':
                    LOG.warning("Build %s for job %s failed. No tests to "
                                "fetch", build['number'], job_name)
                    continue

                # Get the tests for this build
                try:
                    tests_found = self.send_request(
                        item=f"job/{job_name}/{build['number']}/testReport",
                        query='')
                except JenkinsError as jerr:
                    if '404' in str(jerr):
                        LOG.warning("No tests found for build %s for job %s",
                                    build['number'], job_name)
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

                    for test in suit['cases']:
                        if not test['className']:
                            continue

                        # Duration comes in seconds (float)
                        duration_in_ms = test.get('duration')*1000
                        job_objects[job_name].builds[build['number']].add_test(
                            Test(name=test.get('name'),
                                 class_name=test.get('className'),
                                 result=test.get('status'),
                                 duration=duration_in_ms))

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def job_missing_deployment_info(self, job: Dict[str, str]):
        """Check if a given Jenkins job has all deployment attributes.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        :returns: Whether all deployment attributes are found in the job
        :rtype bool:
        """
        for attr in self.deployment_attr:
            if attr not in job:
                return True
        return False

    @speed_index({'base': 2})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from jenkins server.

        :returns: container of jobs with deployment information from
        jenkins server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.send_request(self.jobs_last_build_query)["jobs"]
        jobs_found = filter_jobs(jobs_found, **kwargs)

        use_artifacts = True
        if len(jobs_found) > 12:
            LOG.warning("Requesting deployment information for %d jobs \
will be based on the job name and approximate, restrict the query for more \
accurate results", len(jobs_found))
            use_artifacts = False

        job_deployment_info = []
        for job in jobs_found:
            last_build = job.get("lastBuild")
            if use_artifacts and last_build is not None:
                # if we have a lastBuild, we will have artifacts to pull
                self.add_job_info_from_artifacts(job)
            else:
                self.add_job_info_from_name(job)
            job_deployment_info.append(job)

        checks_to_apply = []
        for attribute in self.deployment_attr:
            # check for user provided that should have an exact match
            input_attr = kwargs.get(attribute)
            if input_attr and input_attr.value:
                checks_to_apply.append(partial(satisfy_exact_match,
                                       user_input=input_attr,
                                       field_to_check=attribute))

        input_controllers = kwargs.get('controllers')
        if input_controllers and input_controllers.value:
            for range_arg in input_controllers.value:
                operator, value = range_arg
                checks_to_apply.append(partial(filter_topology,
                                       operator=operator,
                                       value=value,
                                       component='controller'))

        input_computes = kwargs.get('computes')
        if input_computes and input_computes.value:
            for range_arg in input_computes.value:
                operator, value = range_arg
                checks_to_apply.append(partial(filter_topology,
                                       operator=operator,
                                       value=value,
                                       component='compute'))

        job_deployment_info = apply_filters(job_deployment_info,
                                            *checks_to_apply)

        job_objects = {}
        for job in job_deployment_info:
            name = job.get('name')
            job_objects[name] = Job(name=name, url=job.get('url'))
            topology = job["topology"]
            nodes = {}
            if topology:
                for component in topology.split(","):
                    role, amount = component.split(":")
                    for i in range(int(amount)):
                        node_name = role+f"-{i}"
                        nodes[node_name] = Node(node_name, role=role)

            # TODO: (jgilaber) query for services
            deployment = Deployment(job["release"],
                                    job["infra_type"],
                                    nodes, {}, ip_version=job["ip_version"],
                                    topology=topology,
                                    network_backend=job["network_backend"],
                                    storage_backend=job["storage_backend"],
                                    dvr=job["dvr"],
                                    tls_everywhere=job["tls_everywhere"])
            job_objects[name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def add_job_info_from_artifacts(self, job: Dict[str, str]):
        """Add information to the job by querying the last build artifacts.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        possible_artifacts = ["artifacts/jp.env", ".sh/run.sh", ".envrc"]
        job_name = job['name']
        artifact = None
        for artifact_path in possible_artifacts:
            artifact_url = f"job/{job_name}/lastBuild/artifact/{artifact_path}"
            try:
                artifact = self.send_request(item=artifact_url, query="",
                                             api_entrypoint="",
                                             raw_response=True)
                break
            except JenkinsError:
                LOG.debug("Found no artifact %s for job %s", artifact_path,
                          job_name)
                continue

        if artifact is None:
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job)
            return

        for line in artifact.split("\n"):
            if "TOPOLOGY=" in line:
                topology_str = detect_job_info_regex(line, PROPERTY_PATTERN,
                                                     group_index=1)
                topology_str = topology_str.replace('"', '')
                topology_str = topology_str.replace("'", '')
                job["topology"] = topology_str
            if "--version" in line:
                job["release"] = detect_job_info_regex(line,
                                                       RELEASE_RUN)
            if "PRODUCT_VERSION" in line:
                job["release"] = detect_job_info_regex(line,
                                                       RELEASE_VERSION)

            if "--storage-backend" in line or "STORAGE_BACKEND" in line:
                storage = detect_job_info_regex(line, STORAGE_BACKEND_PATTERN)
                job["storage_backend"] = storage

            if "--network-backend" in line or "NETWORK_BACKEND" in line:
                network = detect_job_info_regex(line, NETWORK_BACKEND_PATTERN)
                job["network_backend"] = network

            if "--network-protocol" in line or "NETWORK_PROTOCOL" in line:
                job["ip_version"] = detect_job_info_regex(job_name, IP_PATTERN,
                                                          group_index=1,
                                                          default="unknown")
            if "--network-dvr" in line:
                dvr_option = detect_job_info_regex(line, DVR_PATTERN_RUN,
                                                   group_index=1)
                job["dvr"] = ""
                if dvr_option:
                    job["dvr"] = str(dvr_option in ('true', 'yes'))

            if "NETWORK_DVR" in line:
                dvr_option = detect_job_info_regex(line, OPTIONS)
                job["dvr"] = ""
                if dvr_option:
                    job["dvr"] = str(dvr_option in ('true', 'yes'))

            if "--tls-everywhere" in line:
                tls_option = detect_job_info_regex(line, TLS_PATTERN_RUN,
                                                   group_index=1)
                job["tls_everywhere"] = ""
                if tls_option:
                    job["tls_everywhere"] = str(tls_option in ('true', 'yes'))

            if "TLS_EVERYWHERE" in line:
                tls_option = detect_job_info_regex(line, OPTIONS)
                job["tls_everywhere"] = ""
                if tls_option:
                    job["tls_everywhere"] = str(tls_option in ('true', 'yes'))

        if self.job_missing_deployment_info(job):
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job)

    def add_job_info_from_name(self, job:  Dict[str, str]):
        """Add information to the job by using regex on the job name. Check if
        properties exist before adding them in case it's used as fallback when
        artifacts do not contain all the necessary information.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        job_name = job['name']
        if "topology" not in job or not job["topology"]:
            short_topology = detect_job_info_regex(job_name,
                                                   TOPOLOGY_PATTERN)
            if short_topology:
                # due to the regex used, short_topology may contain a trailing
                # underscore that should be removed
                short_topology = short_topology.rstrip("_")
                job["topology"] = translate_topology_string(short_topology)
            else:
                job["topology"] = ""

        if "release" not in job or not job["release"]:
            job["release"] = detect_job_info_regex(job_name,
                                                   RELEASE_PATTERN)

        if "infra_type" not in job or not job["infra_type"]:
            infra_type = detect_job_info_regex(job_name,
                                               DEPLOYMENT_PATTERN)
            if not infra_type and "virt" in job_name:
                infra_type = "virt"
            job["infra_type"] = infra_type

        if "network_backend" not in job or not job["network_backend"]:
            network_backend = detect_job_info_regex(job_name,
                                                    NETWORK_BACKEND_PATTERN)
            job["network_backend"] = network_backend

        if "storage_backend" not in job or not job["storage_backend"]:
            storage_backend = detect_job_info_regex(job_name,
                                                    STORAGE_BACKEND_PATTERN)
            job["storage_backend"] = storage_backend

        if "ip_version" not in job or not job["ip_version"]:
            job["ip_version"] = detect_job_info_regex(job_name, IP_PATTERN,
                                                      group_index=1,
                                                      default="unknown")
        if "dvr" not in job or not job["dvr"]:
            dvr = detect_job_info_regex(job_name, DVR_PATTERN_NAME)
            job["dvr"] = ""
            if dvr:
                job["dvr"] = str(dvr == "dvr")

        if "tls_everywhere" not in job or not job["tls_everywhere"]:
            # some jobs have TLS in their name as upper case
            job["tls_everywhere"] = ""
            if "tls" in job_name.lower():
                job["tls_everywhere"] = "True"
