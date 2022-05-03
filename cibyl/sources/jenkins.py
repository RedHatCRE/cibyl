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
import os
import re
from functools import partial
from typing import Dict, List
from urllib.parse import urlparse

import requests
import urllib3
import yaml

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.models.ci.test import Test
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.utils import translate_topology_string
from cibyl.sources.server import ServerSource
from cibyl.sources.source import safe_request_generic, speed_index
from cibyl.utils.dicts import subset
from cibyl.utils.filtering import (DEPLOYMENT_PATTERN, DVR_PATTERN_NAME,
                                   IP_PATTERN, NETWORK_BACKEND_PATTERN,
                                   RELEASE_PATTERN, SERVICES_PATTERN,
                                   STORAGE_BACKEND_PATTERN, TOPOLOGY_PATTERN,
                                   apply_filters, filter_topology,
                                   satisfy_case_insensitive_match,
                                   satisfy_exact_match, satisfy_range_match,
                                   satisfy_regex_match)

LOG = logging.getLogger(__name__)

safe_request = partial(safe_request_generic, custom_error=JenkinsError)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def filter_nodes(job: dict, user_input: Argument, field_to_check: str):
    """Check whether job should be included according to the user input. The
    model should be added if the node models provided in the field designated
    by the variable field_to_check are present in the user_input values.

    :param job: job information obtained from jenkins
    :type job: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    valid_nodes = 0
    for node in job['nodes'].values():
        attr = getattr(node, field_to_check)
        attr.value = subset(attr.value, user_input.value)
        valid_nodes += len(attr)
    # if the subset is empty, job should be filtered
    return valid_nodes > 0


def filter_models_by_name(job: dict, user_input: Argument,
                          field_to_check: str):
    """Check whether job should be included according to the user input. The
    model should be added if the models provided in the field designated by the
    variable field_to_check are present in the user_input values.

    :param job: job information obtained from jenkins
    :type job: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    job[field_to_check] = subset(job[field_to_check], user_input.value)
    # if the subset is empty, job should be filtered
    return bool(job[field_to_check])


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
    if build_status and build_status.value:
        checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=build_status,
                                       field_to_check="result"))

    for build in builds_found:
        # ensure that the build number is passed as a string, Jenkins usually
        # sends it as an int
        build["number"] = str(build["number"])

    return apply_filters(builds_found, *checks_to_apply)


def is_test(test):
    """Check if a given test representation corresponds to a test and not
    to some container returned by Jenkins.

    :param test: Jenkins Job representation as a dictionary
    :type test: dict
    :returns: Whether the test representation actually corresponds to a test
    :rtype: bool
    """
    # If the test does not have a className, then it is a container
    return bool(test['className'])


def filter_tests(tests_found: List[Dict], **kwargs):
    """Filter the tests obtainedfrom the Jenkins API according to
    user input."""
    checks_to_apply = [is_test]

    tests_arg = kwargs.get('tests')
    if tests_arg:
        pattern = re.compile("|".join(tests_arg.value))
        checks_to_apply.append(partial(satisfy_regex_match, pattern=pattern,
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

    return apply_filters(tests_found, *checks_to_apply)


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
        self.deployment_attr = ["topology", "release",
                                "network_backend", "storage_backend",
                                "infra_type", "dvr", "ip_version",
                                "tls_everywhere"]

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

            :returns: container of jobs with the selected build(s)
             and their tests
            :rtype: :class:`AttributeDictValue`
        """

        self.check_builds_for_test(**kwargs)

        jobs_found = self.get_builds(**kwargs)

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

                    tests_filtered = filter_tests(suit['cases'], **kwargs)
                    for test in tests_filtered:

                        # Duration comes in seconds (float)
                        duration_in_ms = test.get('duration')*1000
                        build.add_test(
                            Test(name=test.get('name'),
                                 class_name=test.get('className'),
                                 result=test.get('status'),
                                 duration=duration_in_ms))

        return AttributeDictValue("jobs", attr_type=Job, value=jobs_found)

    def job_missing_deployment_info(self, job: Dict[str, str]):
        """Check if a given Jenkins job has all deployment attributes.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        :returns: Whether all deployment attributes are found in the job
        :rtype bool:
        """
        for attr in self.deployment_attr:
            if attr not in job or not job[attr]:
                return True
        return False

    @speed_index({'base': 2})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from jenkins server.

        :returns: container of jobs with deployment information from
        jenkins server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.send_request(self.jobs_query_for_deployment)["jobs"]
        jobs_found = filter_jobs(jobs_found, **kwargs)

        spec = "spec" in kwargs
        use_artifacts = True
        if len(jobs_found) > 1 and spec:
            raise JenkinsError("Full Openstack specification can be shown "
                               "only for one job, please restrict the query.")
        if len(jobs_found) > 12:
            LOG.warning("Requesting deployment information for %d jobs \
will be based on the job name and approximate, restrict the query for more \
accurate results", len(jobs_found))
            use_artifacts = False

        job_deployment_info = []
        for job in jobs_found:
            last_build = job.get("lastCompletedBuild")
            if spec:
                if last_build is None:
                    # jenkins only has a logs link for completed builds
                    raise JenkinsError("Openstack specification requested for"
                                       f" job {job['name']} but job has no "
                                       "completed build.")
                else:
                    self.add_job_info_from_artifacts(job, query_packages=True,
                                                     query_containers=True,
                                                     query_services=True)
            elif use_artifacts and last_build is not None:
                # if we have a lastBuild, we will have artifacts to pull
                containers = "containers" in kwargs
                packages = "packages" in kwargs
                services = "services" in kwargs
                self.add_job_info_from_artifacts(job,
                                                 query_packages=packages,
                                                 query_containers=containers,
                                                 query_services=services)
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

        input_services = kwargs.get('services')
        if input_services and input_services.value:
            checks_to_apply.append(partial(filter_models_by_name,
                                           field_to_check='services',
                                           user_input=input_services))

        for attribute in ['containers', 'packages']:
            input_attr = kwargs.get(attribute)
            if input_attr and input_attr.value:
                checks_to_apply.append(partial(filter_nodes,
                                       user_input=input_attr,
                                       field_to_check=attribute))

        job_deployment_info = apply_filters(job_deployment_info,
                                            *checks_to_apply)

        job_objects = {}
        for job in job_deployment_info:
            name = job.get('name')
            job_objects[name] = Job(name=name, url=job.get('url'))
            topology = job["topology"]
            if not job.get("nodes") and topology:
                job["nodes"] = {}
                for component in topology.split(","):
                    role, amount = component.split(":")
                    for i in range(int(amount)):
                        node_name = role+f"-{i}"
                        job["nodes"][node_name] = Node(node_name, role=role)

            deployment = Deployment(job["release"],
                                    job["infra_type"],
                                    nodes=job.get("nodes", {}),
                                    services=job.get("services", {}),
                                    ip_version=job["ip_version"],
                                    topology=topology,
                                    network_backend=job["network_backend"],
                                    storage_backend=job["storage_backend"],
                                    dvr=job["dvr"],
                                    tls_everywhere=job["tls_everywhere"])
            job_objects[name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def add_job_info_from_artifacts(self, job: dict,
                                    query_packages: bool = False,
                                    query_services: bool = False,
                                    query_containers: bool = False):
        """Add information to the job by querying the last build artifacts.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        :param query_packages: Whether to provide package information
        :type query_packages: bool
        :param query_containers: Whether to provide container information
        :type query_containers: bool
        :param query_services: Whether to provide services information
        :type query_services: bool
        """
        job_name = job['name']
        build_description = job["lastCompletedBuild"].get("description")
        if not build_description:
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job)
            return
        logs_url_pattern = re.compile(r'href="(.*)">Browse logs')
        logs_url = logs_url_pattern.search(build_description)
        if logs_url is None:
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job)
            return
        logs_url = logs_url.group(1)

        artifact_path = "infrared/provision.yml"
        artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
        try:
            artifact = self.send_request(item="", query="",
                                         url=artifact_url,
                                         raw_response=True)
            artifact = yaml.safe_load(artifact)
            nodes = artifact['provision']['topology'].get('nodes', {})
            topology = []
            for node_path, amount in nodes.items():
                node = os.path.split(node_path)[1]
                node = os.path.splitext(node)[0]
                topology.append(f"{node}:{amount}")
            job["topology"] = ",".join(topology)

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)

        artifact_path = "infrared/overcloud-install.yml"
        artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
        try:
            artifact = self.send_request(item="", query="",
                                         url=artifact_url,
                                         raw_response=True)
            artifact = yaml.safe_load(artifact)
            overcloud = artifact.get('install', {})
            job["release"] = overcloud.get("version", "")
            deployment = overcloud.get('deployment', {})
            job["infra_type"] = os.path.split(deployment.get('files', ""))[1]
            storage = overcloud.get("storage", {})
            job["storage_backend"] = storage.get("backend", "")
            network = overcloud.get("network", {})
            job["network_backend"] = network.get("backend", "")
            ip_string = network.get("protocol", "")
            job["ip_version"] = detect_job_info_regex(ip_string, IP_PATTERN,
                                                      group_index=1,
                                                      default="unknown")
            job["dvr"] = str(network.get("dvr", ""))
            tls = overcloud.get("tls", {})
            job["tls_everywhere"] = str(tls.get("everywhere", ""))

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)

        if not job.get("topology", ""):
            self.get_topology_from_job_name(job)
        topology = job["topology"]
        job["nodes"] = {}
        if topology:
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    containers = {}
                    packages = {}
                    if query_packages:
                        packages = self.get_packages_node(node_name,
                                                          logs_url,
                                                          job_name)
                    if query_containers:
                        containers = self.get_containers_node(node_name,
                                                              logs_url,
                                                              job_name)
                    job["nodes"][node_name] = Node(node_name, role=role,
                                                   containers=containers,
                                                   packages=packages)

        artifact_path = "undercloud-0/var/log/extra/services.txt.gz"
        artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
        job["services"] = {}
        if query_services:
            try:
                artifact = self.send_request(item="", query="",
                                             url=artifact_url,
                                             raw_response=True)
                for service in SERVICES_PATTERN.findall(artifact):
                    job["services"][service] = Service(service)

            except JenkinsError:
                LOG.debug("Found no artifact %s for job %s", artifact_path,
                          job_name)

        if self.job_missing_deployment_info(job):
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job)

    def get_packages_node(self, node_name, logs_url, job_name):
        """Get a list of packages installed in a openstack node from the job
        logs.

        :params node_name: Name of the node to inspect
        :type node_name: str
        :params logs_url: Url of the job's logs
        :type logs_url: str
        :params job_name: Name of the job to inspect
        :type job_name: str

        :returns: Packages found in the node
        :rtype: dict
        """
        artifact_path = "var/log/extra/rpm-list.txt.gz"
        artifact_url = f"{logs_url.rstrip('/')}/{node_name}/{artifact_path}"
        packages = {}
        try:
            artifact = self.send_request(item="", query="",
                                         url=artifact_url,
                                         raw_response=True)
            package_list = artifact.rstrip().split("\n")
            for package in package_list:
                packages[package] = Package(package)

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)
        return packages

    def get_packages_container(self, container_name, logs_url, job_name):
        """Get a list of packages installed in a container from the job
        logs.

        :params container_name: Name of the container to inspect
        :type node_name: str
        :params logs_url: Url of the job's logs
        :type logs_url: str
        :params job_name: Name of the job to inspect
        :type job_name: str

        :returns: Packages found in the container
        :rtype: dict
        """
        artifact_path = f"{container_name}/log/dnf.rpm.log.gz"
        artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
        packages = {}
        package_pattern = re.compile(r"SUBDEBUG .*: (.*)")
        try:
            artifact = self.send_request(item="", query="",
                                         url=artifact_url,
                                         raw_response=True)
            for package in package_pattern.findall(artifact):
                packages[package] = Package(package)

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)
        return packages

    def get_containers_node(self, node_name, logs_url, job_name):
        """Get a list of containers used in a openstack node from the job
        logs.

        :params node_name: Name of the node to inspect
        :type node_name: str
        :params logs_url: Url of the job's logs
        :type logs_url: str
        :params job_name: Name of the job to inspect
        :type job_name: str

        :returns: Packages found in the node
        :rtype: dict
        """
        artifact_path = "var/log/extra/podman/containers"
        artifact_url = f"{logs_url}/{node_name}/{artifact_path}"
        containers = {}
        try:
            artifact = self.send_request(item="", query="",
                                         url=artifact_url,
                                         raw_response=True)
            names_pattern = re.compile(r'<a href=\"([\w+/\.]*)\">([\w/]*)</a>')
            for folder in names_pattern.findall(artifact):
                # the page listing the containers has many links, most of them
                # point to folders with container information, which have the
                # same text in the link and the displayed text
                if folder[1] not in folder[0]:
                    continue
                container_name = folder[1].rstrip("/")
                packages = self.get_packages_container(container_name,
                                                       artifact_url,
                                                       job_name)
                containers[container_name] = Container(container_name,
                                                       packages=packages)

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)
        return containers

    def get_topology_from_job_name(self, job: Dict[str, str]):
        """Extract the openstack topology from the job name.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        job_name = job["name"]
        short_topology = detect_job_info_regex(job_name,
                                               TOPOLOGY_PATTERN)
        if short_topology:
            # due to the regex used, short_topology may contain a trailing
            # underscore that should be removed
            short_topology = short_topology.rstrip("_")
            job["topology"] = translate_topology_string(short_topology)
        else:
            job["topology"] = ""

    def add_job_info_from_name(self, job:  Dict[str, str]):
        """Add information to the job by using regex on the job name. Check if
        properties exist before adding them in case it's used as fallback when
        artifacts do not contain all the necessary information.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        job_name = job['name']
        if "topology" not in job or not job["topology"]:
            self.get_topology_from_job_name(job)

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
