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
from unittest import TestCase

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.printers.raw import OSRawPrinter
from cibyl.plugins.openstack.service import Service


class TestOSRawPrinter(TestCase):
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

        deployment = Deployment(release, infra,
                                nodes, services,
                                ip_version=ip_version,
                                topology=topology,
                                network_backend=network,
                                storage_backend=storage,
                                dvr=dvr,
                                tls_everywhere=tls_everywhere)

        printer = OSRawPrinter(verbosity=1)

        result = printer.print_deployment(deployment)

        self.assertIn("Release:", result)
        self.assertIn(release, result)
        self.assertIn("Infra type:", result)
        self.assertIn(infra, result)
        self.assertIn("IP version:", result)
        self.assertIn(ip_version, result)
        self.assertIn("Topology:", result)
        self.assertIn(topology, result)
        self.assertIn("Network backend:", result)
        self.assertIn(network, result)
        self.assertIn("Storage backend:", result)
        self.assertIn(storage, result)
        self.assertIn("DVR:", result)
        self.assertIn(dvr, result)
        self.assertIn("TLS everywhere:", result)
        self.assertIn(tls_everywhere, result)
        self.assertIn("Service name:", result)
        self.assertIn('nova', result)
        self.assertIn("Node name:", result)
        self.assertIn('controller-0', result)


def test_print_node(self):
    """Test that the string representation of Node works.
    """
    name = 'controller-0'
    role = 'controller'
    node = Node(name, role)

    printer = OSRawPrinter(verbosity=1)

    result = printer.print_node(node)

    self.assertIn("Node name:", result)
    self.assertIn(name, result)
    self.assertIn("Role: ", result)
    self.assertIn(role, result)


def test_print_service(self):
    """Test that the string representation of Service works.
    """
    name = 'test-service'
    config = {'option1': 'true'}
    service = Service(name, config)

    printer = OSRawPrinter(verbosity=1)

    result = printer.print_service(service)

    self.assertIn("Service name:", result)
    self.assertIn(name, result)
    self.assertIn("option1:", result)
    self.assertIn("true", result)
