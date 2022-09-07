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
from unittest import TestCase

from cibyl.models.ci.base.stage import Stage
from cibyl.outputs.cli.printer import STDJSON
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.printers.serialized import OSJSONPrinter
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection


class TestOSJSONPrinter(TestCase):
    """Tests for :class:`OSJSONPrinter`.
    """
    def setUp(self):
        self.indentation = 2
        self.provider = STDJSON(indentation=self.indentation)
        self.printer = OSJSONPrinter(provider=self.provider, verbosity=1)

    def test_print_deployment(self):
        """Test that the string representation of Deployment works.
        """
        release = '17.0'
        infra = 'ovb'
        services = {'nova': Service('nova', {})}
        nodes = {'controller-0': Node('controller-0', 'controller')}
        ip_version = "4"
        topology = "controllers:1"
        network = "vxlan"
        storage = "ceph"
        dvr = "true"
        tls_everywhere = "false"
        templates = set(["a", "b"])
        ml2_driver = "ovn"
        ironic = "True"
        cleaning_net = "False"
        security_group = "N/A"
        test_collection = TestCollection(set(["test1", "test2"]), setup="rpm")
        network_obj = Network(ip_version=ip_version, network_backend=network,
                              dvr=dvr, tls_everywhere=tls_everywhere,
                              ml2_driver=ml2_driver,
                              security_group=security_group)
        storage_obj = Storage(cinder_backend=storage)
        ironic_obj = Ironic(ironic_inspector=ironic,
                            cleaning_network=cleaning_net)

        deployment = Deployment(release, infra,
                                nodes, services,
                                network=network_obj,
                                topology=topology,
                                storage=storage_obj,
                                overcloud_templates=templates,
                                ironic=ironic_obj,
                                test_collection=test_collection)

        result = self.printer.print_deployment(deployment)

        expected_network = {
                'ip_version': ip_version, 'network_backend': network,
                'ml2_driver': ml2_driver, 'security_group': security_group,
                "dvr": dvr, 'tls_everywhere': tls_everywhere
        }
        expected_storage = {'cinder_backend': storage}
        expected_ironic = {'ironic_inspector': ironic,
                           'cleaning_network': cleaning_net}
        expected_templates = list(templates)
        expected_tests = {'tests': ['test1', 'test2'], 'setup': 'rpm'}
        expected_nodes = [{'role': 'controller', 'containers': [],
                           'packages': []}]
        expected_services = [{'name': 'nova', 'configuration': {}}]
        expected_obj = {
            "release": release, "infra_type": infra, "topology": topology,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services, "stages": []
        }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_overcloud_templates_not_available(self):
        """Test that overcloud_templates are printed correctly
        when set to N/A."""
        release = '17.0'
        infra = 'ovb'
        deployment = Deployment(release, infra, {}, {},
                                overcloud_templates="N/A")

        result = self.printer.print_deployment(deployment)

        expected_network = {}
        expected_storage = {}
        expected_ironic = {}
        expected_templates = []
        expected_tests = {}
        expected_nodes = []
        expected_services = []
        expected_obj = {
            "release": release, "infra_type": infra, "topology": None,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services, "stages": []
        }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_test_collection_not_available(self):
        """Test that test_collection is printed correctly
        when set to N/A."""
        release = '17.0'
        infra = 'ovb'
        deployment = Deployment(release, infra, {}, {},
                                test_collection="N/A")

        result = self.printer.print_deployment(deployment)

        expected_network = {}
        expected_storage = {}
        expected_ironic = {}
        expected_templates = []
        expected_tests = {'tests': [], 'setup': None}
        expected_nodes = []
        expected_services = []
        expected_obj = {
            "release": release, "infra_type": infra, "topology": None,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services, "stages": []
        }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_empty_deployment(self):
        """Test that the string representation of an empty deployment shows the
        apropiate message.
        """
        deployment = Deployment("", "", {}, {})
        result = self.printer.print_deployment(deployment)

        expected_network = {}
        expected_storage = {}
        expected_ironic = {}
        expected_templates = []
        expected_tests = {}
        expected_nodes = []
        expected_services = []
        expected_obj = {
            "release": "", "infra_type": "", "topology": None,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services, "stages": []
        }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_deployment_missing_information(self):
        """Test that the string representation of Deployment skips the missing
        information.
        """
        release = '17.0'
        infra = 'ovb'
        nodes = {'controller-0': Node('controller-0', 'controller')}
        ip_version = "4"
        topology = "controllers:1"
        network = "vxlan"
        storage = "ceph"
        dvr = "true"
        tls_everywhere = "false"
        templates = set(["a", "b"])
        ml2_driver = "ovn"
        ironic = "N/A"
        cleaning_net = "N/A"
        security_group = "N/A"
        test_collection = "N/A"
        network_obj = Network(ip_version=ip_version, network_backend=network,
                              dvr=dvr, tls_everywhere=tls_everywhere,
                              ml2_driver=ml2_driver,
                              security_group=security_group)
        storage_obj = Storage(cinder_backend=storage)
        ironic_obj = Ironic(ironic_inspector=ironic,
                            cleaning_network=cleaning_net)

        deployment = Deployment(release, infra,
                                nodes, {},
                                topology=topology,
                                network=network_obj,
                                overcloud_templates=templates,
                                storage=storage_obj,
                                ironic=ironic_obj,
                                test_collection=test_collection)

        expected_tests = {'tests': [], 'setup': None}
        expected_network = {
                'ip_version': ip_version, 'network_backend': network,
                'ml2_driver': ml2_driver, 'security_group': security_group,
                "dvr": dvr, 'tls_everywhere': tls_everywhere
        }
        expected_storage = {'cinder_backend': storage}
        expected_ironic = {'ironic_inspector': ironic,
                           'cleaning_network': cleaning_net}
        expected_templates = list(templates)
        expected_nodes = [{'role': 'controller', 'containers': [],
                           'packages': []}]
        expected_services = []
        expected_obj = {
            "release": release, "infra_type": infra, "topology": topology,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services, "stages": []
        }
        result = self.printer.print_deployment(deployment)

        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_node(self):
        """Test that the string representation of Node works.
        """
        name = 'controller-0'
        role = 'controller'
        packages = {"rpm-package": Package("rpm-package", "rhos-release")}
        containers = {"container": Container("container", "image")}
        node = Node(name, role, containers=containers, packages=packages)

        result = self.printer.print_node(node)
        expected_obj = {
                'role': role,
                'containers': [{'name': 'container', 'image': 'image',
                               'packages': []}],
                'packages': [{'name': 'rpm-package', 'origin': 'rhos-release'}]
        }

        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_service(self):
        """Test that the string representation of Service works.
        """
        name = 'test-service'
        config = {'option1': 'true'}
        service = Service(name, config)

        result = self.printer.print_service(service)
        expected_obj = {'name': 'test-service',
                        'configuration': {'option1': 'true'}}
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_package(self):
        """Test that the string representation of Package works."""
        name = "rpm-package"
        origin = "rhos-release"
        package = Package(name, origin)

        result = self.printer.print_package(package)
        expected_obj = {'name': 'rpm-package', 'origin': 'rhos-release'}
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_container(self):
        """Test that the string representation of Package works."""
        name = "container"
        image = "image"
        packages = {"rpm-package": Package("rpm-package", "rhos-release")}
        container = Container(name, image, packages)

        result = self.printer.print_container(container)
        expected_obj = {'name': name, 'image': image,
                        'packages': [{'name': 'rpm-package',
                                      'origin': 'rhos-release'}]
                        }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_collection(self):
        """Test that the string representation of TestCollection works."""
        collection = TestCollection(set(["test1", "test2"]), setup="rpm")

        result = self.printer.print_test_collection(collection)
        expected_obj = {'tests': ['test1', 'test2'], 'setup': 'rpm'}
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)

    def test_print_stages(self):
        """Test that the string representation of Stage within a
        deployment works."""
        stages = [Stage("Build", "FAILED", 60e3),
                  Stage("Run", "SUCCESS", 120e3)]
        deployment = Deployment("17.0", "virt", {}, {}, stages=stages)

        result = self.printer.print_deployment(deployment)
        expected_network = {}
        expected_storage = {}
        expected_ironic = {}
        expected_templates = []
        expected_tests = {}
        expected_nodes = []
        expected_services = []
        expected_obj = {
            "release": "17.0", "infra_type": "virt", "topology": None,
            "network": expected_network, "storage": expected_storage,
            "ironic": expected_ironic,
            "overcloud_templates": expected_templates,
            "test_collection": expected_tests, "nodes": expected_nodes,
            "services": expected_services,
            "stages": [{'name': "Build", 'status': "FAILED",
                        'duration': 60000.0},
                       {'name': "Run", 'status': "SUCCESS",
                        'duration': 120000.0}]
            }
        expected = json.dumps(expected_obj, indent=self.indentation)
        self.assertEqual(result, expected)
