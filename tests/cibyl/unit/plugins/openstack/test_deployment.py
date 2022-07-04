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

from cibyl.models.ci.base.stage import Stage
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection


class TestOpenstackDeployment(TestCase):
    """Test openstack deployment model."""
    def setUp(self):
        self.release = '17.0'
        self.infra = 'ovb'
        self.services = {'nova': Service('nova', {})}
        self.nodes = {'controller-0': Node('controller-0', 'controller')}
        self.ip_version = "4"
        self.topology = "controllers:1"
        self.network = "vxlan"
        self.storage = "ceph"
        self.dvr = "true"
        self.tls_everywhere = "false"
        self.templates = set(["a", "b", "c"])
        self.ml2_driver = "ovn"
        self.ironic = "True"
        self.cleaning_net = "False"
        self.security_group = "native ovn"
        self.network_obj = Network(ip_version=self.ip_version,
                                   network_backend=self.network,
                                   dvr=self.dvr, ml2_driver=self.ml2_driver,
                                   tls_everywhere=self.tls_everywhere,
                                   security_group=self.security_group)
        self.storage_obj = Storage(cinder_backend=self.storage)
        self.ironic_obj = Ironic(ironic_inspector=self.ironic,
                                 cleaning_network=self.cleaning_net)

        self.deployment = Deployment(self.release, self.infra, {}, {})
        self.second_deployment = Deployment(self.release, self.infra,
                                            self.nodes,
                                            self.services,
                                            topology=self.topology,
                                            network=self.network_obj,
                                            storage=self.storage_obj,
                                            ironic=self.ironic_obj,
                                            overcloud_templates=self.templates)

    def test_merge_method(self):
        """Test merge method of Deployment class."""
        self.assertIsNone(self.deployment.network.value)
        self.assertEqual({}, self.deployment.services.value)
        self.assertEqual({}, self.deployment.nodes.value)
        self.second_deployment.add_stage(Stage("Run", "SUCCESS"))
        self.deployment.merge(self.second_deployment)

        network = self.deployment.network.value
        storage = self.deployment.storage.value
        ironic = self.deployment.ironic.value
        self.assertEqual(self.nodes, self.deployment.nodes.value)
        self.assertEqual(self.services, self.deployment.services.value)
        self.assertEqual(self.topology, self.deployment.topology.value)
        self.assertEqual(self.templates,
                         self.deployment.overcloud_templates.value)
        self.assertEqual(self.ip_version, network.ip_version.value)
        self.assertEqual(self.network, network.network_backend.value)
        self.assertEqual(self.dvr, network.dvr.value)
        self.assertEqual(self.tls_everywhere, network.tls_everywhere.value)
        self.assertEqual(self.ml2_driver, network.ml2_driver.value)
        self.assertEqual(self.storage, storage.cinder_backend.value)
        self.assertEqual(self.ironic, ironic.ironic_inspector.value)
        self.assertEqual(self.cleaning_net, ironic.cleaning_network.value)
        self.assertEqual(self.security_group, network.security_group.value)
        self.assertEqual(len(self.deployment.stages), 1)
        stage_obj = self.deployment.stages[0]
        self.assertEqual(stage_obj.name.value, "Run")
        self.assertEqual(stage_obj.status.value, "SUCCESS")

    def test_merge_method_existing_templates(self):
        """Test merge method of Deployment class with both deployments having
        templates."""
        deployment = Deployment(self.release, self.infra, {}, {},
                                overcloud_templates=set(["d"]))
        deployment.merge(self.second_deployment)
        self.assertEqual(deployment.overcloud_templates.value,
                         set(["a", "b", "c", "d"]))

    def test_add_node(self):
        """Test add_node method of Deployment class."""
        self.assertEqual({}, self.deployment.nodes.value)
        self.deployment.add_node(self.nodes['controller-0'])
        self.assertEqual(self.nodes, self.deployment.nodes.value)

    def test_add_service(self):
        """Test add_service method of Deployment class."""
        self.assertEqual({}, self.deployment.services.value)
        self.deployment.add_service(self.services['nova'])
        self.assertEqual(self.services, self.deployment.services.value)

    def test_merge_method_existing_service(self):
        """Test merge method of Deployment class."""

        service_to_add = Service('nova', {'option': 'false'})
        self.deployment.add_service(service_to_add)
        self.second_deployment.merge(self.deployment)
        service = self.second_deployment.services.value['nova']
        self.assertEqual(service.name.value, service_to_add.name.value)
        self.assertEqual(service.configuration.value,
                         service_to_add.configuration.value)

    def test_merge_method_existing_node(self):
        """Test merge method of Deployment class."""

        node_to_add = Node('controller-0', 'controller',
                           packages={'package': Package('package')})
        self.deployment.add_node(node_to_add)
        self.second_deployment.merge(self.deployment)
        node = self.second_deployment.nodes['controller-0']
        self.assertEqual(node.name.value, node.name.value)
        self.assertEqual(node.role.value, node.role.value)
        self.assertEqual(node.packages['package'].name,
                         node_to_add.packages['package'].name)

    def test_merge_method_existing_test_collection(self):
        """Test merge method of Deployment class."""
        test_collection = TestCollection(set(["test1", "test2"]))
        test_collection2 = TestCollection(set(["test3"]))
        deployment = Deployment(self.release, self.infra, {}, {},
                                test_collection=test_collection)
        deployment2 = Deployment(self.release, self.infra, {}, {},
                                 test_collection=test_collection2)
        deployment2.merge(deployment)
        test_collection = deployment2.test_collection.value
        tests = test_collection.tests.value
        self.assertEqual(len(tests), 3)
        self.assertIn("test1", tests)
        self.assertIn("test2", tests)
        self.assertIn("test3", tests)

    def test_merge_method_non_existing_test_collection(self):
        """Test merge method of Deployment class."""
        test_collection = TestCollection(set(["test1", "test2"]))
        deployment = Deployment(self.release, self.infra, {}, {},
                                test_collection=test_collection)
        deployment2 = Deployment(self.release, self.infra, {}, {})
        deployment2.merge(deployment)
        test_collection = deployment2.test_collection.value
        tests = test_collection.tests.value
        self.assertEqual(len(tests), 2)
        self.assertIn("test1", tests)
        self.assertIn("test2", tests)
