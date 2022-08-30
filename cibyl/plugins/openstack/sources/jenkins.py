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

import os
import re
from functools import partial
from typing import Dict, Tuple, Union

import yaml

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection
from cibyl.plugins.openstack.utils import translate_topology_string
from cibyl.sources.jenkins import LOG, detect_job_info_regex, filter_jobs
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source import speed_index
from cibyl.utils.dicts import subset
from cibyl.utils.files import get_file_name_from_path
from cibyl.utils.filtering import (CINDER_BACKEND_PATTERN, DEPLOYMENT_PATTERN,
                                   DVR_PATTERN_NAME, IP_PATTERN,
                                   NETWORK_BACKEND_PATTERN, RELEASE_PATTERN,
                                   SERVICES_PATTERN, TOPOLOGY_PATTERN,
                                   apply_filters, filter_topology,
                                   satisfy_case_insensitive_match,
                                   satisfy_exact_match, satisfy_regex_match)

# shorthand for the type that will hold the job information obtained from the
# Jenkins API response
JenkinsJob = Dict[str, Union[dict, str]]


def filter_models_by_name(job: dict, user_input: Argument,
                          field_to_check: str) -> bool:
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


def should_query_for_nodes_topology(**kwargs) -> Tuple[bool, bool]:
    """Check the user cli arguments to ascertain whether we should query for
    nodes and the topology value of a deployment.
    :returns: Whether we should query for nodes and topology
    :rtype: bool, bool
    """
    spec = "spec" in kwargs
    query_nodes = "nodes" in kwargs or "controllers" in kwargs
    query_nodes |= "computes" in kwargs
    query_nodes |= "packages" in kwargs or "containers" in kwargs
    # query_topology stores whether there is any argument that will require
    # the topology to be queried, which might be the topology itself, or
    # any information about the nodes, containers or packages or the spec
    # argument
    query_topology = "topology" in kwargs or spec or query_nodes
    return query_nodes, query_topology


def filter_test_collection(job: JenkinsJob, user_input: Argument) -> bool:
    """Check whether job should be included according to user input. The model
    should be added if the test_setup attribute of the TestCollection matches
    the value passed by the user. If the job does not have any test information
    it should be excluded as well."""
    tests = job.get("test_collection")
    if tests is None:
        return False
    return tests.setup.value in user_input.value


def filter_nodes(job: JenkinsJob, user_input: Argument,
                 field_to_check: str) -> bool:
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
    for node in job.get('nodes', {}).values():
        attr = getattr(node, field_to_check)
        attr.value = subset(attr.value, user_input.value)
        valid_nodes += len(attr)
    # if the subset is empty, job should be filtered
    return valid_nodes > 0


def filter_models_set_field(job: JenkinsJob, user_input: Argument,
                            field_to_check: str) -> bool:
    """Check whether job should be included according to the user input. The
    model should be added if the models provided in the field designated
    by the variable field_to_check (represented by a set)
    are present in the user_input values.

    :param job: job information obtained from jenkins
    :type job: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    if not isinstance(job[field_to_check], set):
        # if the field_to_check is not a set, the model should not be included
        return False
    job[field_to_check].intersection_update(set(user_input.value))
    # if the subset is empty, job should be filtered
    return bool(job[field_to_check])


class Jenkins(SourceExtension):
    """A class representation of Jenkins client."""

    deployment_attr = ["topology", "release",
                       "network_backend", "cinder_backend",
                       "infra_type", "dvr", "ip_version",
                       "tls_everywhere", "ml2_driver",
                       "ironic_inspector", "test_setup"]

    # deployment properties that have no cli argument and will not be used to
    # filter jobs, just for the spec
    spec_params = ["cleaning_network", "security_group", "overcloud_templates",
                   "test_collection", "tls_everywhere"]
    possible_attributes = deployment_attr+spec_params

    def add_job_info_from_name(self, job: JenkinsJob, **kwargs) -> None:
        """Add information to the job by using regex on the job name. Check if
        properties exist before adding them in case it's used as fallback when
        artifacts do not contain all the necessary information.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        :param spec: Whether to provide full spec information
        :type spec: bool
        """
        spec = "spec" in kwargs
        job_name = job['name']
        _, query_topology = should_query_for_nodes_topology(**kwargs)
        missing_topology = "topology" not in job or not job["topology"]
        if missing_topology and query_topology:
            self.get_topology_from_job_name(job)

        missing_release = "release" not in job or not job["release"]
        if missing_release and ("release" in kwargs or spec):
            job["release"] = detect_job_info_regex(job_name,
                                                   RELEASE_PATTERN)

        missing_infra_type = "infra_type" not in job or not job["infra_type"]
        if missing_infra_type and ("infra_type" in kwargs or spec):
            infra_type = detect_job_info_regex(job_name,
                                               DEPLOYMENT_PATTERN)
            if not infra_type and "virt" in job_name:
                infra_type = "virt"
            job["infra_type"] = infra_type

        missing_network_backend = not bool(job.get("network_backend", ""))
        if missing_network_backend and ("network_backend" in kwargs or spec):
            network_backend = detect_job_info_regex(job_name,
                                                    NETWORK_BACKEND_PATTERN)
            job["network_backend"] = network_backend

        missing_cinder_backend = not bool(job.get("cinder_backend", ""))
        if missing_cinder_backend and ("cinder_backend" in kwargs or spec):
            cinder_backend = detect_job_info_regex(job_name,
                                                   CINDER_BACKEND_PATTERN)
            job["cinder_backend"] = cinder_backend

        missing_ip_version = "ip_version" not in job or not job["ip_version"]
        if missing_ip_version and ("ip_version" in kwargs or spec):
            job["ip_version"] = detect_job_info_regex(job_name, IP_PATTERN,
                                                      group_index=1,
                                                      default="unknown")
        missing_dvr = "dvr" not in job or not job["dvr"]
        if missing_dvr and ("dvr" in kwargs or spec):
            dvr = detect_job_info_regex(job_name, DVR_PATTERN_NAME)
            job["dvr"] = ""
            if dvr:
                job["dvr"] = str(dvr == "dvr")

        missing_tls_everywhere = not bool(job.get("tls_everywhere", ""))
        if missing_tls_everywhere and ("tls_everywhere" in kwargs or spec):
            # some jobs have TLS in their name as upper case
            job["tls_everywhere"] = ""
            if "tls" in job_name.lower():
                job["tls_everywhere"] = "True"

        topology = job.get("topology")
        if not job.get("nodes") and "nodes" in kwargs and topology:
            job["nodes"] = {}
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    job["nodes"][node_name] = Node(node_name, role=role)

    def job_missing_deployment_info(self, job: JenkinsJob, **kwargs) -> bool:
        """Check if a given Jenkins job has all deployment attributes.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        :returns: Whether all deployment attributes are found in the job
        :rtype bool:
        """
        spec = "spec" in kwargs
        for attr in self.possible_attributes:
            should_query = spec or attr in kwargs
            if should_query and (attr not in job or not job[attr]):
                return True
        return False

    @speed_index({'base': 2, 'release': 3, 'infra_type': 3, 'spec': 3,
                  'ironic_inspector': 3, 'controllers': 3, 'computes': 3,
                  'ml2_driver': 3, 'containers': 3, 'services': 3})
    def get_deployment(self, **kwargs) -> AttributeDictValue:
        """Get deployment information for jobs from jenkins server.

        :returns: container of jobs with deployment information from
        jenkins server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.send_request(self.jobs_query_for_deployment)["jobs"]

        spec = "spec" in kwargs

        jobs_found = filter_jobs(jobs_found, **kwargs)
        if spec:
            self.check_jobs_for_spec(jobs_found, **kwargs)

        use_artifacts = True
        if len(jobs_found) > 12:
            LOG.warning("Requesting deployment information for %d jobs \
will be based on the job name and approximate, restrict the query for more \
accurate results", len(jobs_found))
            use_artifacts = False

        job_deployment_info = []
        for job in jobs_found:
            job_name = job['name']
            last_build = job.get("lastCompletedBuild")
            if spec:
                if last_build is None:
                    # jenkins only has a logs link for completed builds
                    raise JenkinsError("Openstack specification requested for"
                                       f" job {job_name} but job has no "
                                       "completed build.")
                else:
                    self.add_job_info_from_artifacts(job, **kwargs)
            elif use_artifacts and last_build is not None:
                # if we have a lastBuild, we will have artifacts to pull
                self.add_job_info_from_artifacts(job, **kwargs)
            else:
                self.add_job_info_from_name(job, **kwargs)
            if "stages" in kwargs:
                if not last_build:
                    msg = "No build was found for job %s, information about "
                    msg += "stages will not be shown for it."
                    LOG.warning(msg, job_name)
                else:
                    job["stages"] = self._get_stages(job_name,
                                                     last_build["number"])

            job_deployment_info.append(job)

        checks_to_apply = []
        for attribute in self.deployment_attr:
            # check for user provided that should have an exact match
            input_attr = kwargs.get(attribute)
            if attribute in ('dvr', 'tls_everywhere') and input_attr:
                checks_to_apply.append(partial(satisfy_case_insensitive_match,
                                       user_input=input_attr,
                                       field_to_check=attribute,
                                       default_user_value=['True']))
                continue
            if attribute in ('release', 'topology') and input_attr:
                for pattern_str in input_attr.value:
                    pattern = re.compile(pattern_str)
                    checks_to_apply.append(partial(satisfy_regex_match,
                                                   pattern=pattern,
                                                   field_to_check=attribute))
                continue
            if attribute == 'test_setup' and input_attr:
                checks_to_apply.append(partial(filter_test_collection,
                                               user_input=input_attr))
                continue
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
        # filter by templates
        input_overcloud_templates = kwargs.get('overcloud_templates')
        if input_overcloud_templates and input_overcloud_templates.value:
            check = partial(filter_models_set_field,
                            field_to_check="overcloud_templates",
                            user_input=input_overcloud_templates)
            checks_to_apply.append(check)

        for attribute in ('containers', 'packages'):
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
            topology = ""
            if "topology" in kwargs or spec:
                # since querying for topology is used as a prequisite to
                # querying for any node-related information (packages,
                # containers, ...) make sure that the user asked for it before
                # adding it
                topology = job.get("topology", "")
            network_backend = job.get("network_backend", "")
            cinder_backend = job.get("cinder_backend", "")
            tls_everywhere = job.get("tls_everywhere", "")
            ironic_inspector = job.get("ironic_inspector", "")
            cleaning_network = job.get("cleaning_network", "")
            security_group = job.get("security_group", "")
            overcloud_templates = job.get("overcloud_templates")
            test_collection = job.get("test_collection")
            network = Network(ip_version=job.get("ip_version", ""),
                              ml2_driver=job.get("ml2_driver", ""),
                              network_backend=network_backend,
                              dvr=job.get("dvr", ""),
                              tls_everywhere=tls_everywhere,
                              security_group=security_group)
            storage = Storage(cinder_backend=cinder_backend)
            ironic = Ironic(ironic_inspector=ironic_inspector,
                            cleaning_network=cleaning_network)

            deployment = Deployment(job.get("release", ""),
                                    job.get("infra_type", ""),
                                    nodes=job.get("nodes", {}),
                                    services=job.get("services", {}),
                                    topology=topology,
                                    network=network,
                                    storage=storage,
                                    ironic=ironic,
                                    test_collection=test_collection,
                                    overcloud_templates=overcloud_templates,
                                    stages=job.get("stages"))
            job_objects[name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def add_job_info_from_artifacts(self, job: JenkinsJob, **kwargs) -> None:
        """Add information to the job by querying the last build artifacts.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        spec = "spec" in kwargs
        query_nodes, query_topology = should_query_for_nodes_topology(**kwargs)
        job_name = job['name']
        build_description = job["lastCompletedBuild"].get("description")
        if not build_description:
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job, **kwargs)
            return
        logs_url_pattern = re.compile(r'href="(.*)">Browse logs')
        logs_url = logs_url_pattern.search(build_description)
        if logs_url is None:
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job, **kwargs)
            return
        logs_url = logs_url.group(1)

        if query_topology:
            artifact_path = "infrared/provision.yml"
            artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
            try:
                artifact = self.send_request(item="", query="",
                                             url=artifact_url,
                                             raw_response=True)
                artifact = yaml.safe_load(artifact)
                provision = artifact.get('provision', {})
                nodes = provision.get('topology', {}).get('nodes', {})
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
            if "release" in kwargs or spec:
                job["release"] = overcloud.get("version", "")
            deployment = overcloud.get('deployment', {})
            if "infra_type" in kwargs or spec:
                infra = deployment.get('files', "")
                if infra is not None:
                    infra = os.path.split(infra)[1]
                job["infra_type"] = infra
            storage = overcloud.get("storage", {})
            if "cinder_backend" in kwargs or spec:
                job["cinder_backend"] = storage.get("backend", "")
            network = overcloud.get("network", {})
            if "network_backend" in kwargs or spec:
                job["network_backend"] = network.get("backend", "")
            ip_string = network.get("protocol", "")
            if "ip_version" in kwargs or spec:
                job["ip_version"] = detect_job_info_regex(ip_string,
                                                          IP_PATTERN,
                                                          group_index=1,
                                                          default="unknown")
            if "dvr" in kwargs or spec:
                job["dvr"] = str(network.get("dvr", ""))
            if "tls_everywhere" in kwargs or spec:
                tls = overcloud.get("tls", {})
                tls_value = tls.get("everywhere", "")
                if tls_value is not None:
                    # tls everywhere is encoded a a bool in the artifacts, we
                    # want to store it as a string
                    job["tls_everywhere"] = str(tls_value)
            if "ml2_driver" in kwargs or spec:
                job["ml2_driver"] = "ovn"
                if network.get("ovs"):
                    job["ml2_driver"] = "ovs"
            if "ironic_inspector" in kwargs or spec:
                job["ironic_inspector"] = str(overcloud.get("ironic_inspector",
                                                            False))
            if "overcloud_templates" in kwargs or spec:
                job["overcloud_templates"] = set()
                overcloud_params = overcloud.get("overcloud", {})
                templates = overcloud_params.get("templates", [])
                templates_found = set()
                for template in templates:
                    template_name = get_file_name_from_path(template)
                    if template_name != "none":
                        templates_found.add(template_name)
                if templates_found:
                    job["overcloud_templates"] = templates_found

            if spec:
                cleaning = overcloud.get("cleaning", {})
                job["cleaning_network"] = str(cleaning.get("network", ""))
                config = overcloud.get("config", {})
                heat = config.get("heat", {})
                job["security_group"] = heat.get("NeutronOVSFirewallDriver",
                                                 "")

        except JenkinsError:
            LOG.debug("Found no artifact %s for job %s", artifact_path,
                      job_name)

        test_setup = "test_setup" in kwargs
        if spec or test_setup:
            artifact_path = "infrared/test.yml"
            artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
            try:
                artifact = self.send_request(item="", query="",
                                             url=artifact_url,
                                             raw_response=True)
                artifact = yaml.safe_load(artifact)
                test = artifact.get("test", {})
                tests = []
                setup = test.get("setup")
                if spec:
                    tests = test.get("tests", [])
                test_names = {get_file_name_from_path(test) for test in tests}
                job["test_collection"] = TestCollection(test_names, setup)

            except JenkinsError:
                LOG.debug("Found no artifact %s for job %s", artifact_path,
                          job_name)

        if query_topology:
            if not job.get("topology", ""):
                self.get_topology_from_job_name(job)
            topology = job["topology"]
            if query_nodes:
                job["nodes"] = {}
                if topology:
                    for component in topology.split(","):
                        role, amount = component.split(":")
                        for i in range(int(amount)):
                            node_name = role+f"-{i}"
                            container = {}
                            packages = {}
                            if "packages" in kwargs and not spec:
                                packages = self.get_packages_node(node_name,
                                                                  logs_url,
                                                                  job_name)
                            if "containers" in kwargs and not spec:
                                container = self.get_containers_node(node_name,
                                                                     logs_url,
                                                                     job_name)
                            node = Node(node_name, role=role,
                                        containers=container,
                                        packages=packages)
                            job["nodes"][node_name] = node

        artifact_path = "undercloud-0/var/log/extra/services.txt.gz"
        artifact_url = f"{logs_url.rstrip('/')}/{artifact_path}"
        job["services"] = {}
        if "services" in kwargs and not spec:
            try:
                artifact = self.send_request(item="", query="",
                                             url=artifact_url,
                                             raw_response=True)
                for service in SERVICES_PATTERN.findall(artifact):
                    job["services"][service] = Service(service)

            except JenkinsError:
                LOG.debug("Found no artifact %s for job %s", artifact_path,
                          job_name)

        if self.job_missing_deployment_info(job, **kwargs):
            LOG.debug("Resorting to get deployment information from job name"
                      " for job %s", job_name)
            self.add_job_info_from_name(job, **kwargs)
            release = job.get("release")
            query_ml2_driver = (spec or "ml2_driver" in kwargs)
            if query_ml2_driver and release and not job.get("ml2_driver"):
                # ovn is the default starting from OSP 15.0
                if float(release) > 15.0:
                    job["ml2_driver"] = "ovn"
                else:
                    job["ml2_driver"] = "ovs"
            LOG.warning("Some logs are missing for job %s, information "
                        "will be retrieved from the job name, but will "
                        "be incomplete", job_name)
            if spec and not job.get("security_group"):
                ml2_driver = job["ml2_driver"]
                if ml2_driver == "ovn":
                    job["security_group"] = "native ovn"
                else:
                    job["security_group"] = "iptables hybrid"
            if spec:
                self.add_unable_to_find_info_message(job)

    def get_packages_node(self, node_name: str, logs_url: str,
                          job_name: str) -> Dict[str, Package]:
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

    def get_packages_container(self, container_name: str, logs_url: str,
                               job_name: str) -> Dict[str, Package]:
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

    def get_containers_node(self, node_name: str, logs_url: str,
                            job_name: str) -> Dict[str, Container]:
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

    def get_topology_from_job_name(self, job: JenkinsJob) -> None:
        """Extract the openstack topology from the job name.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        job_name = job["name"]
        short_topology = detect_job_info_regex(job_name,
                                               TOPOLOGY_PATTERN,
                                               group_index=1)
        if short_topology:
            # due to the regex used, short_topology may contain a trailing
            # underscore that should be removed
            short_topology = short_topology.rstrip("_")
            job["topology"] = translate_topology_string(short_topology)
        else:
            job["topology"] = ""

    def add_unable_to_find_info_message(self, job: JenkinsJob) -> None:
        """Set a message explaining the reason for missing fields in spec.

        :param job: Dictionary representation of a jenkins job
        :type job: dict
        """
        message = "N/A"
        for attr in self.possible_attributes:
            if not job.get(attr):
                job[attr] = message
