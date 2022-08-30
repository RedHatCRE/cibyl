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
# pylint: disable=no-member
import logging
from unittest import TestCase
from unittest.mock import Mock, call

import yaml

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.exceptions.source import InvalidArgument
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.sources.jenkins import (filter_models_by_name,
                                                     filter_models_set_field,
                                                     filter_nodes,
                                                     filter_test_collection)
from cibyl.plugins.openstack.test_collection import TestCollection
from cibyl.sources.jenkins import Jenkins
from tests.cibyl.utils import OpenstackPluginWithJobSystem


def get_yaml_from_topology_string(topology):
    """Transform a topology string into a dictionary of the same format used in
    the infrared provision.yml file.

    :param topology: Topology string in the format node: amount
    :type topology: str

    :returns: yaml representation of a provision.yml file
    :rtype: str
    """
    provision = {'provision': {'topology': {}}}
    if not topology:
        return yaml.dump(provision)
    topology_dict = {}
    for component in topology.split(","):
        name, amount = component.split(":")
        topology_dict[name+".yml"] = int(amount)
    provision['provision']['topology']['nodes'] = topology_dict
    return yaml.dump(provision)


def get_yaml_tests(test_suites=None, setup=None):
    """Provide a yaml representation for the parameters obtained from an
    infrared test.yml file.

    :param test_suites: Suites to be run
    :type test_suites: list
    :param setup: Source of setup packages
    :type setup: str
    """
    test_dict = {'tests': []}
    if test_suites:
        for suite in test_suites:
            test_dict['tests'].append(f"/path/to/suite/{suite}.yml")
    if setup:
        test_dict['setup'] = setup
    return yaml.dump({'test': test_dict})


def get_yaml_overcloud(ip=None, release=None, cinder_backend=None,
                       network_backend=None, dvr=None,
                       tls_everywhere=None, infra_type=None, ml2_driver=None,
                       ironic_inspector=None, cleaning_network=None,
                       security_group=None, overcloud_templates=None):
    """Provide a yaml representation for the paremeters obtained from an
    infrared overcloud-install.yml file.

    :param ip: Ip version used
    :type ip: str
    :param release: Openstack version used
    :type release: str
    :param cinder_backend: Storage backend used
    :type cinder_backend: str
    :param network_backend: Network backend used
    :type network_backend: str
    :param dvr: Whether dvr is used
    :type dvr: bool
    :param tls_everywhere: Whether tls_everywhere is used
    :type tls_everywhere: bool

    :returns: yaml representation of a overcloud-install.yml file
    :rtype: str
    """
    if ip and ip != "unknown":
        ip = f"ipv{ip}"
    overcloud = {"version": release, }
    overcloud["deployment"] = {"files": infra_type}
    if cinder_backend:
        storage = {"backend": cinder_backend}
        overcloud["storage"] = storage
    network = {}
    if network_backend:
        network["backend"] = network_backend
    if ip:
        network["protocol"] = ip
    if dvr is not None:
        network["dvr"] = dvr
    if ml2_driver == "ovn":
        network["ovn"] = True
        network["ovs"] = False
    elif ml2_driver == "ovs":
        network["ovs"] = True
        network["ovn"] = False
    overcloud["network"] = network
    if tls_everywhere != "":
        tls = {"everywhere": tls_everywhere}
        overcloud["tls"] = tls
    if ironic_inspector:
        overcloud["ironic_inspector"] = True
    overcloud["cleaning"] = {"network": False}
    if cleaning_network:
        overcloud["cleaning"]["network"] = True
    if security_group:
        security_group_dict = {"NeutronOVSFirewallDriver": security_group}
        overcloud["config"] = {"heat": security_group_dict}
    if overcloud_templates:
        overcloud["overcloud"] = {"templates": overcloud_templates}
    return yaml.dump({"install": overcloud})


class TestJenkinsSourceOpenstackPlugin(OpenstackPluginWithJobSystem):
    """Tests for :class:`Jenkins` with openstack plugin."""

    def setUp(self):
        self.jenkins = Jenkins("url", "user", "token")
        logging.disable(logging.CRITICAL)

    def test_get_deployment(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins.
        """
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:1", "compute:1,controller:2", ""]

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            network = deployment.network.value
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(len(deployment.nodes.value), 0)

    def test_get_deployment_many_jobs(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins.
        """
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:1", "compute:1,controller:2", ""]

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})
        for _ in range(12):
            # ensure that there are more than 12 jobs and jenkins source gets
            # deployment information from job name
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': 'test_job', 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])

        args = {
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)

    def test_get_deployment_artifacts_fallback(self):
        """ Test that get_deployment falls back to reading job_names after
        failing to find artifacts.
        """
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:1", "compute:1,controller:2", ""]

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {}})
        # each job triggers 2 artifacts requests, if both fail, fallback to
        # search the name
        artifacts_fail = [JenkinsError for _ in range(3*len(job_names))]
        self.jenkins.send_request = Mock(side_effect=[response]+artifacts_fail)
        self.jenkins.add_job_info_from_name = Mock(
                side_effect=self.jenkins.add_job_info_from_name)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.jenkins.add_job_info_from_name.assert_called()
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)

    def test_get_deployment_artifacts_fallback_no_logs_link(self):
        """ Test that get_deployment falls back to reading job_names after
        failing to find artifacts.
        """
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:1", "compute:1,controller:2", ""]

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            "link"}})
        # each job triggers 2 artifacts requests, if both fail, fallback to
        # search the name
        artifacts_fail = [JenkinsError for _ in range(3*len(job_names))]
        self.jenkins.send_request = Mock(side_effect=[response]+artifacts_fail)
        self.jenkins.add_job_info_from_name = Mock(
                side_effect=self.jenkins.add_job_info_from_name)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.jenkins.add_job_info_from_name.assert_called()
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)

    def test_get_deployment_artifacts(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        services = """
tripleo_heat_api_cron.service loaded    active     running
tripleo_heat_engine.service loaded    active     running
tripleo_ironic_api.service loaded    active     running
tripleo_ironic_conductor.service loaded    active     running
        """
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")]
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(5*2))
        artifacts.extend([services])
        artifacts.extend([
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(3*2))
        artifacts.extend([services])

        artifacts.extend([
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(4*2))
        artifacts.extend([services])

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "services": Argument("services", str, "", value=[]),
            "packages": Argument("packages", str, "", value=[]),
            "containers": Argument("containers", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=['False']),
            "tls_everywhere": Argument("tls_everywhere", str, "",
                                       value=['False']),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            storage = deployment.storage.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(storage.cinder_backend.value, "ceph")
            self.assertEqual(network.network_backend.value, "geneve")
            self.assertEqual(network.dvr.value, "False")
            self.assertEqual(network.tls_everywhere.value, "False")
            self.assertEqual(deployment.infra_type.value, "ovb")
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    node = Node(node_name, role)
                    node_found = deployment.nodes[node_name]
                    self.assertEqual(node_found.name, node.name)
                    self.assertEqual(node_found.role, node.role)
            services = deployment.services
            self.assertTrue("tripleo_heat_api_cron" in services.value)
            self.assertTrue("tripleo_heat_engine" in services.value)
            self.assertTrue("tripleo_ironic_api" in services.value)
            self.assertTrue("tripleo_ironic_conductor" in services.value)

    def test_get_deployment_ip_version_artifacts(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_job', 'test_16_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        services = """
tripleo_heat_api_cron.service loaded    active     running
tripleo_heat_engine.service loaded    active     running
tripleo_ironic_api.service loaded    active     running
tripleo_ironic_conductor.service loaded    active     running
        """
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")]
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(5*2))
        artifacts.extend([services])
        artifacts.extend([
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(3*2))
        artifacts.extend([services])

        artifacts.extend([
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(4*2))
        artifacts.extend([services])

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "services": Argument("services", str, "", value=[]),
            "packages": Argument("packages", str, "", value=[]),
            "containers": Argument("containers", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            storage = deployment.storage.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(storage.cinder_backend.value, "ceph")
            self.assertEqual(network.network_backend.value, "")
            self.assertEqual(network.dvr.value, "")
            self.assertEqual(network.tls_everywhere.value, "")
            self.assertEqual(deployment.infra_type.value, "ovb")
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    node = Node(node_name, role)
                    node_found = deployment.nodes[node_name]
                    self.assertEqual(node_found.name, node.name)
                    self.assertEqual(node_found.role, node.role)
            services = deployment.services
            self.assertTrue("tripleo_heat_api_cron" in services.value)
            self.assertTrue("tripleo_heat_engine" in services.value)
            self.assertTrue("tripleo_ironic_api" in services.value)
            self.assertTrue("tripleo_ironic_conductor" in services.value)

    def test_get_deployment_artifacts_all_missing(self):
        """ Test that get_deployment handles properly the case where the logs
        do not contain the relevant information.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [JenkinsError()]*12

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
            "services": Argument("services", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release in zip(job_names, ip_versions, releases):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            storage = deployment.storage.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, "")
            self.assertEqual(storage.cinder_backend.value, "")
            self.assertEqual(network.network_backend.value, "")
            self.assertEqual(network.dvr.value, "")
            self.assertEqual(network.tls_everywhere.value, "")
            self.assertEqual(deployment.infra_type.value, "")
            self.assertEqual(deployment.nodes.value, {})
            self.assertEqual(deployment.services.value, {})

    def test_get_deployment_artifacts_missing_property(self):
        """ Test that get_deployment detects missing information from
        jenkins artifacts.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["", "", ""]
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': {}})
        artifacts = [
           f"bla\nJP_TOPOLOGY='{topologies[0]}'\nPRODUCT_VERSION=17.3",
           f"bla\nJP_TOPOLOGY='{topologies[1]}'\nPRODUCT_VERSION=16",
           f"bla\nJP_TOPOLOGY='{topologies[2]}'\nPRODUCT_VERSION=",
            ]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)
        args = {
            "release": Argument("release", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "topology": Argument("topology", str, "", value=[]),
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)

    def test_get_deployment_filter_ipv(self):
        """Test that get_deployment filters by ip_version."""
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        args = {
            "ip_version": Argument("ip_version", str, "", value=["4"])
        }
        self.jenkins.send_request = Mock(side_effect=[response])

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "4")
        self.assertEqual(deployment.topology.value, "")

    def test_get_deployment_job_names_nodes(self):
        """ Test that get_deployment reads properly the information obtained
        from job names from jenkins and provides the nodes when passed the
        --nodes flag.
        """
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        nodes = [["compute-0", "compute-1", "controller-0"],
                 ["compute-0", "controller-0", "controller-1"]]

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "nodes": Argument("nodes", str, "", value=[]),
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, node_list in zip(job_names, nodes):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, "")
            self.assertEqual(network.ip_version.value, "")
            self.assertEqual(deployment.topology.value, "")
            self.assertEqual(len(deployment.nodes.value), len(node_list))
            for node_name, node_expected in zip(deployment.nodes, node_list):
                node = deployment.nodes[node_name]
                self.assertEqual(node.name.value, node_expected)
                self.assertEqual(node.role.value, node_expected.split("-")[0])

    def test_get_deployment_filter_topology(self):
        """Test that get_deployment filters by topology."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        topology_value = "compute:2,controller:1"
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "topology": Argument("topology", str, "", value=[topology_value])
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, topology_value)

    def test_get_deployment_filter_topology_regex(self):
        """Test that get_deployment filters by topology."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        topology_value = "compute:2,controller:1"
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "topology": Argument("topology", str, "",
                                 value=["comp", "controller:1"])
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, topology_value)

    def test_get_deployment_filter_release(self):
        """Test that get_deployment filters by release."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])

        args = {
            "release": Argument("release", str, "", value=["17"])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "17.3")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")

    def test_get_deployment_filter_topology_ip_version(self):
        """Test that get_deployment filters by topology and ip version."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        topology_value = "compute:2,controller:1"
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "ip_version": Argument("ip_version", str, "", value=["6"]),
            "topology": Argument("topology", str, "", value=[topology_value])
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 0)

    def test_get_deployment_filter_network_backend(self):
        """Test that get_deployment filters by network backend."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont_geneve',
                     'test_16_ipv6_job_1comp_2cont_vxlan', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "network_backend": Argument("network_backend", str, "",
                                        value=["geneve"])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont_geneve'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")
        self.assertEqual(network.network_backend.value, "geneve")

    def test_get_deployment_filter_cinder_backend(self):
        """Test that get_deployment filters by storage backend."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont_geneve_swift',
                     'test_16_ipv6_job_1comp_2cont_lvm', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "cinder_backend": Argument("cinder_backend", str, "",
                                       value=["swift"])
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont_geneve_swift'
        job = jobs[job_name]
        deployment = job.deployment.value
        storage = deployment.storage.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")
        self.assertEqual(storage.cinder_backend.value, "swift")
        self.assertEqual(network.network_backend.value, "")

    def test_get_deployment_filter_controller(self):
        """Test that get_deployment filters by controller."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        arg = Argument("controllers", arg_type=str, description="",
                       value=["<2"], ranged=True)

        jobs = self.jenkins.get_deployment(controllers=arg)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")

    def test_get_deployment_filter_computes(self):
        """Test that get_deployment filters by computes."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        arg = Argument("compute", arg_type=str, description="", value=["2"],
                       ranged=True)

        jobs = self.jenkins.get_deployment(computes=arg)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")

    def test_get_deployment_filter_infra_type(self):
        """Test that get_deployment filters by infra type."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont_ovb',
                     'test_16_ipv6_job_1comp_2cont_virt', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])
        args = {
            "infra_type": Argument("infra_type", str, "", value=["ovb"])
        }

        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont_ovb'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")
        self.assertEqual(deployment.infra_type.value, "ovb")

    def test_get_deployment_filter_dvr(self):
        """Test that get_deployment filters by dvr using a case-insensitive
        matching."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont_no_dvr',
                     'test_16_ipv6_job_1comp_2cont_dvr', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])

        args = {
            "dvr": Argument("dvr", str, "", value=["false"])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont_no_dvr'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")
        self.assertEqual(network.dvr.value, "False")

    def test_get_deployment_artifacts_ironic_inspector(self):
        """ Test that get_deployment filters by ironic_inspector."""
        job_name = 'test_17.3_ipv4_job'
        ip_version = '4'
        release = '17.3'
        dvr_status = 'True'
        topology = "compute:2,controller:3"

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        artifacts = [
                get_yaml_from_topology_string(topology),
                get_yaml_overcloud(ip_version, release,
                                   "ceph", "geneve", dvr_status, False, "",
                                   ironic_inspector=True),
                JenkinsError()]  # mock test.yaml

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ironic_inspector": Argument("ironic_inspector", str, "",
                                         value=["True"]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = "test_17.3_ipv4_job"
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        ironic = deployment.ironic.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, release)
        self.assertEqual(network.ip_version.value, ip_version)
        self.assertEqual(deployment.topology.value, topology)
        self.assertEqual(ironic.ironic_inspector.value, "True")

    def test_get_deployment_artifacts_dvr(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        dvr_status = ['True', 'True', 'True']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", dvr_status[0], False, ""),
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", dvr_status[1],
                                   False, ""),
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", dvr_status[2],
                                   False, "")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=[]),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology, dvr in zip(job_names, ip_versions,
                                                        releases, topologies,
                                                        dvr_status):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(network.dvr.value, dvr)

    def test_get_deployment_filter_ml2_driver(self):
        """ Test that get_deployment filters properly according to the value of
        the ml2_driver.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        dvr_status = ['True', 'True', 'True']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", dvr_status[0], False, "",
                                   ml2_driver="ovs"),
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", dvr_status[1],
                                   False, "", ml2_driver="ovn"),
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", dvr_status[2],
                                   False, "")]
        # one call to get_packages_node and get_containers_node per node, plus
        # one to get_services

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=[]),
            "ml2_driver": Argument("ml2_driver", str, "", value=["ovs"]),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = "test_17.3_ipv4_job"
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, releases[0])
        self.assertEqual(network.ip_version.value, ip_versions[0])
        self.assertEqual(deployment.topology.value, topologies[0])
        self.assertEqual(network.dvr.value, dvr_status[0])
        self.assertEqual(network.ml2_driver.value, "ovs")

    def test_get_deployment_filter_overcloud_templates(self):
        """ Test that get_deployment filters properly according to the value of
        the overcloud_templates.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        dvr_status = ['True', 'True', 'True']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", dvr_status[0], False, "",
                                   ml2_driver="ovs",
                                   overcloud_templates=["a", "b"]),
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", dvr_status[1],
                                   False, "", ml2_driver="ovn",
                                   overcloud_templates=["c"]),
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", dvr_status[2],
                                   False, "")]
        # one call to get_packages_node and get_containers_node per node, plus
        # one to get_services

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=[]),
            "ml2_driver": Argument("ml2_driver", str, "", value=[]),
            "overcloud_templates": Argument("overcloud_templates", str, "",
                                            value=["a"]),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = "test_17.3_ipv4_job"
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, releases[0])
        self.assertEqual(network.ip_version.value, ip_versions[0])
        self.assertEqual(deployment.topology.value, topologies[0])
        self.assertEqual(network.dvr.value, dvr_status[0])
        self.assertEqual(network.ml2_driver.value, "ovs")
        self.assertEqual(deployment.overcloud_templates.value, set(["a"]))

    def test_get_deployment_filter_tls(self):
        """Test that get_deployment filters by tls_everywhere."""
        job_names = ['test_17.3_ipv4_job_2comp_1cont_tls',
                     'test_16_ipv6_job_1comp_2cont', 'test_job']
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastBuild': None})

        self.jenkins.send_request = Mock(side_effect=[response])

        args = {
            "tls_everywhere": Argument("tls_everywhere", str, "",
                                       value=["True"])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        job_name = 'test_17.3_ipv4_job_2comp_1cont_tls'
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(deployment.topology.value, "")
        self.assertEqual(network.tls_everywhere.value, "True")

    def test_get_deployment_artifacts_tls(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        tls_status = ['True', 'True', 'True']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        logs_url = 'href="link">Browse logs'
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False, tls_status[0], ""),
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", False,
                                   tls_status[1], ""),
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", False,
                                   tls_status[2], "")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=['False']),
            "tls_everywhere": Argument("tls_everywhere", str, "", value=[]),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology, tls in zip(job_names, ip_versions,
                                                        releases, topologies,
                                                        tls_status):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(network.tls_everywhere.value, tls)

    def test_get_deployment_artifacts_missing_topology(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_ipv4_2comp_3cont_job',
                     'test_16_ipv6_1comp_2cont_job', 'test_2comp_2cont_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        tls_status = ['True', 'True', 'True']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        logs_url = 'href="link">Browse logs'
        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        artifacts = [
                get_yaml_from_topology_string(""),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False, tls_status[0], ""),
                get_yaml_from_topology_string(""),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", False,
                                   tls_status[1], ""),
                get_yaml_from_topology_string(""),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", False,
                                   tls_status[2], "")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "tls_everywhere": Argument("tls_everywhere", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology, tls in zip(job_names, ip_versions,
                                                        releases, topologies,
                                                        tls_status):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(network.tls_everywhere.value, tls)

    def test_get_packages_node(self):
        """ Test that get_packages_node reads properly the information obtained
        from jenkins using artifacts.
        """
        response = """
acl-2.2.53-1.el8.x86_64
aide-0.16-14.el8_4.1.x86_64
ansible-2.9.27-1.el8ae.noarch
ansible-pacemaker-1.0.4-2.20210623224811.666f706.el8ost.noarch
audit-3.0-0.17.20191104git1c2f876.el8.x86_64
audit-libs-3.0-0.17.20191104git1c2f876.el8.x86_64
augeas-libs-1.12.0-6.el8.x86_64
authselect-1.2.2-2.el8.x86_64
authselect-compat-1.2.2-2.el8.x86_64
authselect-libs-1.2.2-2.el8.x86_64
autofs-5.1.4-48.el8_4.1.x86_64
autogen-libopts-5.18.12-8.el8.x86_64
avahi-libs-0.7-20.el8.x86_64
basesystem-11-5.el8.noarch"""
        packages_expected = response.split("\n")

        self.jenkins.send_request = Mock(side_effect=[response])

        url = "url/node/var/log/extra/rpm-list.txt.gz"
        packages = self.jenkins.get_packages_node("node", "url", "job-name")
        self.jenkins.send_request.assert_called_with(query="", item="",
                                                     raw_response=True,
                                                     url=url)
        self.assertEqual(len(packages), len(packages_expected))
        for package, package_name in zip(packages.values(), packages_expected):
            self.assertEqual(package.name.value, package_name)

    def test_get_packages_container(self):
        """ Test that get_packages_container reads properly the information
        obtained from jenkins using artifacts.
        """
        response = """
2022-03-28T14:27:24+00 SUBDEBUG Installed: crudini-0.9-11.el8ost.1
2022-03-28T14:27:30+00 INFO --- logging initialized ---
2022-03-28T14:28:32+00 INFO warning: /etc/sudoers created as /etc/sudoers.rw
2022-03-28T14:31:28+00 SUBDEBUG Upgrade: openssl-libs-1:1.1.1g-16.el8_4
2022-03-28T14:31:28+00 SUBDEBUG Upgraded: python3-dateutil-1:2.6.1-6.el8"""

        packages_expected = ["crudini-0.9-11.el8ost.1",
                             "openssl-libs-1:1.1.1g-16.el8_4",
                             "python3-dateutil-1:2.6.1-6.el8"]

        self.jenkins.send_request = Mock(side_effect=[response])

        url = "url/container/log/dnf.rpm.log.gz"
        packages = self.jenkins.get_packages_container("container", "url",
                                                       "job-name")
        self.jenkins.send_request.assert_called_with(query="", item="",
                                                     raw_response=True,
                                                     url=url)
        self.assertEqual(len(packages), len(packages_expected))
        for package, package_name in zip(packages.values(), packages_expected):
            self.assertEqual(package.name.value, package_name)

    def test_get_packages_container_raises(self):
        """ Test that get_packages_container returns an empty dictionary after
        an error is raised by send_request."""
        self.jenkins.send_request = Mock(side_effect=JenkinsError)

        packages = self.jenkins.get_packages_container("container", "", "")
        self.assertEqual(packages, {})

    def test_get_containers_node(self):
        """ Test that get_containers_node reads properly the information
        obtained from jenkins using artifacts.
        """
        response = """
<a href="./nova_libvirt/">nova_libvirt/</a>
<a href="./nova_libvirt/">nova/</a>
<a href="./nova_migration_target/">nova_migration_target/</a>
"""

        containers_expected = ["nova_libvirt", "nova_migration_target"]

        self.jenkins.send_request = Mock(side_effect=[response, JenkinsError(),
                                                      JenkinsError()])
        base_url = "url/node/var/log/extra/podman/containers"
        urls = [base_url,
                f"{base_url}/nova_libvirt/log/dnf.rpm.log.gz",
                f"{base_url}/nova_migration_target/log/dnf.rpm.log.gz"]

        containers = self.jenkins.get_containers_node("node", "url",
                                                      "job-name")
        calls = [call(item="", query="", url=url,
                      raw_response=True) for url in urls]

        self.jenkins.send_request.assert_has_calls(calls)
        self.assertEqual(len(containers), len(containers_expected))
        for container, container_name in zip(containers.values(),
                                             containers_expected):
            self.assertEqual(container.name.value, container_name)
            self.assertEqual(container.packages.value, {})

    def test_get_deployment_artifacts_filter_services(self):
        """ Test that get_deployment reads properly the information obtained
        from jenkins using artifacts.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']
        ip_versions = ['4', '6', 'unknown']
        releases = ['17.3', '16', '']
        topologies = ["compute:2,controller:3", "compute:1,controller:2",
                      "compute:2,controller:2"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        services = """
tripleo_heat_api_cron.service loaded    active     running
tripleo_heat_engine.service loaded    active     running
tripleo_ironic_api.service loaded    active     running
tripleo_ironic_conductor.service loaded    active     running
        """
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")]
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(5*2))
        artifacts.extend([services])
        artifacts.extend([
                get_yaml_from_topology_string(topologies[1]),
                get_yaml_overcloud(ip_versions[1], releases[1],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(3*2))
        artifacts.extend([services])

        artifacts.extend([
                get_yaml_from_topology_string(topologies[2]),
                get_yaml_overcloud(ip_versions[2], releases[2],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")])
        # one call to get_packages_node and get_containers_node per node
        artifacts.extend([JenkinsError()]*(4*2))
        artifacts.extend([services])

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "containers": Argument("containers", str, "", value=[]),
            "packages": Argument("packages", str, "", value=[]),
            "services": Argument("services", str, "",
                                 value=['tripleo_heat_engine']),
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=['False']),
            "tls_everywhere": Argument("tls_everywhere", str, "",
                                       value=['False']),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 3)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            storage = deployment.storage.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(deployment.infra_type.value, "ovb")
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(storage.cinder_backend.value, "ceph")
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(network.network_backend.value, "geneve")
            self.assertEqual(network.dvr.value, "False")
            self.assertEqual(network.tls_everywhere.value, "False")
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    node = Node(node_name, role)
                    node_found = deployment.nodes[node_name]
                    self.assertEqual(node_found.name, node.name)
                    self.assertEqual(node_found.role, node.role)
            services = deployment.services
            self.assertEqual(len(services), 1)
            self.assertTrue("tripleo_heat_engine" in services.value)

    def test_get_deployment_spec_multiple_jobs(self):
        """ Test that get_deployment fails if --spec is used with
        multiple jobs.
        """
        job_names = ['test_17.3_ipv4_job', 'test_16_ipv6_job', 'test_job']

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        self.jenkins.send_request = Mock(side_effect=[response])

        spec = Argument("spec", str, "", value=job_names)
        self.assertRaises(InvalidArgument, self.jenkins.get_deployment,
                          spec=spec)

    def test_get_deployment_spec_one_job_no_builds(self):
        """ Test that get_deployment fails if --spec is used with a job that
        has no completed builds.
        """
        job_names = ['test_17.3_ipv4_job']

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': None})
        self.jenkins.send_request = Mock(side_effect=[response])

        spec = Argument("spec", str, "", value=['test_17.3_ipv4_job'])
        self.assertRaises(JenkinsError, self.jenkins.get_deployment, spec=spec)

    def test_get_deployment_spec_no_argument(self):
        """ Test that get_deployment fails if --spec is used with a job that
        has no completed builds.
        """
        job_names = ['test_17.3_ipv4_job']

        response = {'jobs': [{'_class': 'folder'}]}
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': None})
        self.jenkins.send_request = Mock(side_effect=[response])

        spec = Argument("spec", str, "", value=[])
        msg = "No job was found, please pass --spec job-name with an "
        msg += " exact match or --jobs job-name with a valid job name "
        msg += "or pattern."
        self.assertRaises(InvalidArgument, self.jenkins.get_deployment,
                          spec=spec, msg=msg)

    def test_get_deployment_spec_correct_call(self):
        """ Test get_deployment call with --spec and one job."""
        job_name = 'test_17.3_ipv4_job'
        ip = '4'
        release = '17.3'
        topology = "compute:2,controller:3"

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topology),
                get_yaml_overcloud(ip, release,
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb",
                                   ironic_inspector=False, ml2_driver="ovs",
                                   cleaning_network=True,
                                   security_group="openvswitch",
                                   overcloud_templates=["a", "b"]),
                get_yaml_tests(["designate", "neutron"])]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        spec = Argument("spec", str, "", value=["test_17.3_ipv4_job"])
        jobs = Argument("jobs", str, "", value=[])

        jobs = self.jenkins.get_deployment(spec=spec, jobs=jobs)
        self.assertEqual(len(jobs), 1)
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        storage = deployment.storage.value
        ironic = deployment.ironic.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, release)
        self.assertEqual(deployment.topology.value, topology)
        self.assertEqual(deployment.infra_type.value, "ovb")
        self.assertEqual(storage.cinder_backend.value, "ceph")
        self.assertEqual(network.ip_version.value, ip)
        self.assertEqual(network.network_backend.value, "geneve")
        self.assertEqual(network.dvr.value, "False")
        self.assertEqual(network.tls_everywhere.value, "False")
        self.assertEqual(network.ml2_driver.value, "ovs")
        self.assertEqual(network.security_group.value, "openvswitch")
        self.assertEqual(ironic.ironic_inspector.value, "False")
        self.assertEqual(ironic.cleaning_network.value, "True")
        self.assertEqual(deployment.overcloud_templates.value,
                         set(["a", "b"]))
        services = deployment.services
        self.assertEqual(len(services), 0)
        test_collection = deployment.test_collection.value
        tests = test_collection.tests.value
        self.assertEqual(len(tests), 2)
        self.assertIn("designate", tests)
        self.assertIn("neutron", tests)
        self.assertIsNone(test_collection.setup.value)

    def test_get_deployment_spec_stages(self):
        """ Test get_deployment call with --spec, --stages and one job."""
        job_name = 'test_17.3_ipv4_job'
        ip_version = '4'
        release = '17.3'
        topology = "compute:2,controller:3"

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url,
                                                        'number': 84}})
        stages_data = {'stages': [{'name': 'build1', 'status': 'SUCCESS'},
                                  {'name': 'run1', 'status': 'FAILURE'}]}
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topology),
                get_yaml_overcloud(ip_version, release,
                                   "ceph", "geneve", dvr=False,
                                   tls_everywhere=False,
                                   infra_type="path/to/ovb",
                                   ironic_inspector=False, ml2_driver="ovs",
                                   cleaning_network=True,
                                   security_group="openvswitch",
                                   overcloud_templates=["a", "b"]),
                JenkinsError,  # mock tests.yaml
                stages_data]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        spec = Argument("spec", str, "", value=[job_name])
        stages = Argument("stages", str, "", value=[])

        jobs = self.jenkins.get_deployment(spec=spec, stages=stages)
        self.assertEqual(len(jobs), 1)
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        storage = deployment.storage.value
        ironic = deployment.ironic.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, release)
        self.assertEqual(network.ip_version.value, ip_version)
        self.assertEqual(deployment.topology.value, topology)
        self.assertEqual(storage.cinder_backend.value, "ceph")
        self.assertEqual(network.network_backend.value, "geneve")
        self.assertEqual(network.dvr.value, "False")
        self.assertEqual(network.tls_everywhere.value, "False")
        self.assertEqual(deployment.infra_type.value, "ovb")
        self.assertEqual(network.ml2_driver.value, "ovs")
        self.assertEqual(ironic.ironic_inspector.value, "False")
        self.assertEqual(ironic.cleaning_network.value, "True")
        self.assertEqual(network.security_group.value, "openvswitch")
        self.assertEqual(deployment.overcloud_templates.value,
                         set(["a", "b"]))
        services = deployment.services
        self.assertEqual(len(services), 0)
        stages = deployment.stages.value
        self.assertEqual(len(stages), 2)
        self.assertEqual(stages[0].name.value, "build1")
        self.assertEqual(stages[0].status.value, "SUCCESS")
        self.assertEqual(stages[1].name.value, "run1")
        self.assertEqual(stages[1].status.value, "FAILURE")

    def test_get_deployment_spec_stages_missing_data(self):
        """ Test get_deployment call with --stages but no
        lastCompletedBuild available."""
        job_name = 'test_17.3_ipv4_job'
        ip_version = '4'

        response = {'jobs': [{'_class': 'folder'}]}
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': None})
        self.jenkins.send_request = Mock(side_effect=[response])
        ip = Argument("ip_version", str, "", value=[])
        stages = Argument("stages", str, "", value=[])

        jobs = self.jenkins.get_deployment(ip_version=ip, stages=stages)
        self.assertEqual(len(jobs), 1)
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "")
        self.assertEqual(network.ip_version.value, ip_version)
        self.assertEqual(deployment.topology.value, "")
        self.jenkins.send_request.assert_called_once()

    def test_get_deployment_spec_correct_call_no_jobs(self):
        """ Test get_deployment call with --spec and one job without using the
        jobs argument."""
        job_name = 'test_17.3_ipv4_job'
        ip = '4'
        release = '17.3'
        topology = "compute:2,controller:3"

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topology),
                get_yaml_overcloud(ip, release,
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb", ml2_driver="ovn"),
                get_yaml_tests(["designate", "neutron"], setup="rpm")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        spec = Argument("spec", str, "", value=["test_17.3_ipv4_job"])
        jobs = self.jenkins.get_deployment(spec=spec)
        self.assertEqual(len(jobs), 1)
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        storage = deployment.storage.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, release)
        self.assertEqual(network.ip_version.value, ip)
        self.assertEqual(deployment.topology.value, topology)
        self.assertEqual(storage.cinder_backend.value, "ceph")
        self.assertEqual(network.network_backend.value, "geneve")
        self.assertEqual(network.dvr.value, "False")
        self.assertEqual(network.ml2_driver.value, "ovn")
        self.assertEqual(network.tls_everywhere.value, "False")
        self.assertEqual(deployment.infra_type.value, "ovb")
        self.assertEqual(network.security_group.value, "native ovn")
        services = deployment.services
        self.assertEqual(len(services), 0)
        test_collection = deployment.test_collection.value
        tests = test_collection.tests.value
        self.assertEqual(len(tests), 2)
        self.assertIn("designate", tests)
        self.assertIn("neutron", tests)
        self.assertEqual(test_collection.setup.value, "rpm")

    def test_get_deployment_spec_no_overcloud_info(self):
        """ Test get_deployment call with --spec and missing overcloud info."""
        job_names = ['test_17.3_ipv4_job']
        topologies = ["compute:2,controller:3"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                JenkinsError,
                JenkinsError]  # mock test.yaml

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        spec = Argument("spec", str, "", value=["test_17.3_ipv4_job"])
        jobs = self.jenkins.get_deployment(spec=spec)
        self.assertEqual(len(jobs), 1)
        job_name = "test_17.3_ipv4_job"
        missing_info = "N/A"
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        ironic = deployment.ironic.value
        storage = deployment.storage.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "17.3")
        self.assertEqual(network.ip_version.value, "4")
        self.assertEqual(deployment.topology.value, topologies[0])
        self.assertEqual(storage.cinder_backend.value, missing_info)
        self.assertEqual(network.network_backend.value, missing_info)
        self.assertEqual(network.dvr.value, missing_info)
        self.assertEqual(network.ml2_driver.value, "ovn")
        self.assertEqual(network.tls_everywhere.value, missing_info)
        self.assertEqual(deployment.infra_type.value, missing_info)
        self.assertEqual(network.security_group.value, "native ovn")
        self.assertEqual(ironic.cleaning_network.value, missing_info)
        self.assertEqual(ironic.ironic_inspector.value, missing_info)

    def test_get_deployment_spec_no_overcloud_info_ovs_default(self):
        """ Test get_deployment call with --spec and missing overcloud info.
        The osp release is set to <15.0 to test that the default ovs is
        assigned properly"""
        job_name = "test_14.3_ipv4_job"
        topologies = ["compute:2,controller:3"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                JenkinsError,
                JenkinsError]  # mock test.yaml

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        spec = Argument("spec", str, "", value=[job_name])
        jobs = self.jenkins.get_deployment(spec=spec)
        self.assertEqual(len(jobs), 1)
        missing_info = "N/A"
        job = jobs[job_name]
        deployment = job.deployment.value
        network = deployment.network.value
        storage = deployment.storage.value
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        self.assertEqual(deployment.release.value, "14.3")
        self.assertEqual(network.ip_version.value, "4")
        self.assertEqual(deployment.topology.value, topologies[0])
        self.assertEqual(storage.cinder_backend.value, missing_info)
        self.assertEqual(network.network_backend.value, missing_info)
        self.assertEqual(network.dvr.value, missing_info)
        self.assertEqual(network.ml2_driver.value, "ovs")
        self.assertEqual(network.tls_everywhere.value, missing_info)
        self.assertEqual(deployment.infra_type.value, missing_info)
        self.assertEqual(network.security_group.value, "iptables hybrid")

    def test_get_deployment_filter_containers(self):
        """ Test get_deployment call with --containers."""
        job_names = ['test_17.3_ipv4_job']
        ip_versions = ['4']
        releases = ['17.3']
        topologies = ["compute:2,controller:3"]

        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        for job_name in job_names:
            response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                     'name': job_name, 'url': 'url',
                                     'lastCompletedBuild': {'description':
                                                            logs_url}})
        containers = """
<a href="./nova_libvirt/">nova_libvirt/</a>
<a href="./nova_libvirt/">nova/</a>
<a href="./nova_migration_target/">nova_migration_target/</a>
"""
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_from_topology_string(topologies[0]),
                get_yaml_overcloud(ip_versions[0], releases[0],
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb")]
        # two call to get_packages_node and get_containers_node per node
        for _ in range(5):
            artifacts.append(containers)
            artifacts.append(JenkinsError())  # get_packages_container
            artifacts.append(JenkinsError())  # get_packages_container

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        args = {
            "containers": Argument("release", str, "", value=["nova_libvirt"]),
            "topology": Argument("topology", str, "", value=[]),
            "release": Argument("release", str, "", value=[]),
            "infra_type": Argument("infra_type", str, "", value=[]),
            "nodes": Argument("nodes", str, "", value=[]),
            "ip_version": Argument("ip_version", str, "", value=[]),
            "dvr": Argument("dvr", str, "", value=['False']),
            "tls_everywhere": Argument("tls_everywhere", str, "",
                                       value=['False']),
            "network_backend": Argument("network_backend", str, "", value=[]),
            "cinder_backend": Argument("cinder_backend", str, "", value=[])
        }
        jobs = self.jenkins.get_deployment(**args)
        self.assertEqual(len(jobs), 1)
        for job_name, ip, release, topology in zip(job_names, ip_versions,
                                                   releases, topologies):
            job = jobs[job_name]
            deployment = job.deployment.value
            network = deployment.network.value
            storage = deployment.storage.value
            self.assertEqual(job.name.value, job_name)
            self.assertEqual(job.url.value, "url")
            self.assertEqual(len(job.builds.value), 0)
            self.assertEqual(deployment.release.value, release)
            self.assertEqual(deployment.topology.value, topology)
            self.assertEqual(network.ip_version.value, ip)
            self.assertEqual(storage.cinder_backend.value, "ceph")
            self.assertEqual(network.network_backend.value, "geneve")
            self.assertEqual(network.dvr.value, "False")
            self.assertEqual(network.tls_everywhere.value, "False")
            self.assertEqual(deployment.infra_type.value, "ovb")
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role+f"-{i}"
                    node = Node(node_name, role)
                    node_found = deployment.nodes[node_name]
                    self.assertEqual(node_found.name, node.name)
                    self.assertEqual(node_found.role, node.role)
                    containers = node_found.containers.value
                    self.assertEqual(len(containers), 1)
                    self.assertIn("nova_libvirt", containers)
            services = deployment.services
            self.assertEqual(len(services), 0)

    def test_get_deployment_test_setup(self):
        """ Test get_deployment call with --test-setup."""
        job_name = 'test_17.3_ipv4_job'
        ip = '4'
        release = '17.3'
        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_overcloud(ip, release,
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb",
                                   ironic_inspector=False, ml2_driver="ovs",
                                   cleaning_network=True,
                                   security_group="openvswitch",
                                   overcloud_templates=["a", "b"]),
                get_yaml_tests(["designate", "neutron"], setup="rpm")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        test_setup = Argument("test_setup", str, "", value=["rpm"])
        jobs = self.jenkins.get_deployment(test_setup=test_setup)
        self.assertEqual(len(jobs), 1)
        job = jobs[job_name]
        self.assertEqual(job.name.value, job_name)
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)
        deployment = job.deployment.value
        network = deployment.network.value
        storage = deployment.storage.value
        ironic = deployment.ironic.value
        self.assertEqual(storage.cinder_backend.value, "")
        self.assertEqual(network.ip_version.value, "")
        self.assertEqual(network.network_backend.value, "")
        self.assertEqual(network.dvr.value, "")
        self.assertEqual(network.tls_everywhere.value, "")
        self.assertEqual(network.ml2_driver.value, "")
        self.assertEqual(network.security_group.value, "")
        self.assertEqual(ironic.ironic_inspector.value, "")
        self.assertEqual(ironic.cleaning_network.value, "")
        test_collection = deployment.test_collection.value
        tests = test_collection.tests.value
        self.assertEqual(len(tests), 0)
        self.assertEqual(test_collection.setup.value, "rpm")

    def test_get_deployment_test_setup_filter(self):
        """ Test get_deployment call with --test-setup, and check that it
        filters jobs that do not matched the value used."""
        job_name = 'test_17.3_ipv4_job'
        ip = '4'
        release = '17.3'
        response = {'jobs': [{'_class': 'folder'}]}
        logs_url = 'href="link">Browse logs'
        response['jobs'].append({'_class': 'org.job.WorkflowJob',
                                 'name': job_name, 'url': 'url',
                                 'lastCompletedBuild': {'description':
                                                        logs_url}})
        # ensure that all deployment properties are found in the artifact so
        # that it does not fallback to reading values from job name
        artifacts = [
                get_yaml_overcloud(ip, release,
                                   "ceph", "geneve", False,
                                   False, "path/to/ovb",
                                   ironic_inspector=False, ml2_driver="ovs",
                                   cleaning_network=True,
                                   security_group="openvswitch",
                                   overcloud_templates=["a", "b"]),
                get_yaml_tests(["designate", "neutron"], setup="rpm")]

        self.jenkins.send_request = Mock(side_effect=[response]+artifacts)

        test_setup = Argument("test_setup", str, "", value=["git"])
        jobs = self.jenkins.get_deployment(test_setup=test_setup)
        self.assertEqual(len(jobs), 0)


class TestFilters(TestCase):
    """Tests for filter functions in jenkins source module."""

    def test_filter_nodes(self):
        """Test that filter_nodes filters nodes according to user input."""
        job = {'nodes': {'node1': Node('node1', 'test',
                                       containers={
                                           'cont1': Container('cont1')}),
                         'node2': Node('node2', 'test',
                                       containers={
                                           'cont2': Container('cont2')})}}
        containers = Mock()
        containers.value = ["cont2"]
        self.assertTrue(filter_nodes(job, containers, 'containers'))
        containers = job['nodes']['node2'].containers.value
        self.assertEqual(containers['cont2'].name.value, 'cont2')
        containers = job['nodes']['node1'].containers.value
        self.assertEqual(containers, {})

    def test_filter_nodes_job_without_nodes(self):
        job = {'name': 'job', 'url': 'url'}
        containers = Mock()
        containers.value = ["cont2"]
        self.assertFalse(filter_nodes(job, containers, 'containers'))

    def test_filter_models_by_name(self):
        """Test that filter_models_by_name filters job according to
        user input."""
        job = {'services': {'service1': Service('service1'),
                            'service2': Service('service2')}}
        services = Mock()
        services.value = ["service2"]
        self.assertTrue(filter_models_by_name(job, services, 'services'))
        self.assertEqual(len(job['services']), 1)
        self.assertIn('service2', job['services'])

    def test_filter_models_set_attribute(self):
        """Test that filter_models_set_field filters job according to user
        input."""
        job = {'templates': set(["a", "b", "c", "d"])}
        template = Mock()
        template.value = ["c", "d"]
        self.assertTrue(filter_models_set_field(job, template, 'templates'))
        self.assertEqual(job["templates"], set(["c", "d"]))

    def test_filter_models_set_attribute_string(self):
        """Test that filter_models_set_field filters job according to user
        input."""
        job = {'templates': "N/A"}
        template = Mock()
        template.value = ["c", "d"]
        self.assertFalse(filter_models_set_field(job, template, 'templates'))
        self.assertEqual(job["templates"], "N/A")

    def test_filter_test_collection(self):
        """Test that filter_test_collection filters jobs according to user
        input."""
        job = {'test_collection': TestCollection(setup="rpm")}
        test_setup = Mock()
        test_setup.value = ["rpm"]
        self.assertTrue(filter_test_collection(job, user_input=test_setup))
        test_setup.value = ["git"]
        self.assertFalse(filter_test_collection(job, user_input=test_setup))
        # test that a job with no TestCollection returns False
        self.assertFalse(filter_test_collection({}, user_input=test_setup))
