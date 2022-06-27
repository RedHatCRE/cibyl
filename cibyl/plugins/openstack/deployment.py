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
from typing import Dict, List

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.stage import Stage
from cibyl.models.model import Model
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.test_collection import TestCollection

# pylint: disable=no-member


class Deployment(Model):
    """Openstack deployment model"""

    API = {
        'release': {
            'attr_type': str,
            'arguments': [Argument(name='--release', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Deployment release version"),
                          Argument(name='--spec', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Print complete openstack"
                                   " deployment")]
        },
        'infra_type': {
            'attr_type': str,
            'arguments': [Argument(name='--infra-type', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Infra type")]
        },
        'nodes': {
            'attr_type': Node,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--nodes', arg_type=str,
                                   nargs='*',
                                   description="Nodes on the deployment"),
                          Argument(name='--controllers', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   ranged=True,
                                   description="Number of controllers used "
                                               "in the deployment"),
                          Argument(name='--computes', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   ranged=True,
                                   description="Number of computes used "
                                               "in the deployment")]
        },
        'services': {
            'attr_type': Service,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--services', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Services in the deployment")]
        },
        'ip_version': {
            'attr_type': str,
            'arguments': [Argument(name='--ip-version', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Ip version used in the "
                                               "deployment")]
        },
        'topology': {
            'attr_type': str,
            'arguments': [Argument(name='--topology', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Topology used in the "
                                               "deployment")]
        },
        'ml2_driver': {
            'attr_type': str,
            'arguments': [Argument(name='--ml2-driver', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="ML2 driver used in the "
                                               "deployment")]
        },
        'cleaning_network': {
            'arguments': []
        },
        'dvr': {
            'arguments': []
        },
        'tls_everywhere': {
            'arguments': []
        },
        'ironic_inspector': {
            'arguments': []
        },
        'security_group': {
            'arguments': []
        },
        'overcloud_templates': {
            'arguments': []
        },
        'test_collection': {
            'attr_type': TestCollection,
            'arguments': []
        },
        'network_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--network-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Network backend used in the "
                                               "deployment")]
        },
        'cinder_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--cinder-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   parent_func='get_jobs',
                                   description="Cinder backend used in the "
                                               "deployment")]
        },
        'stages': {
            'attr_type': Stage,
            'attribute_value_class': AttributeListValue,
            'arguments': []
            }
    }

    def __init__(self, release: str, infra_type: str,
                 nodes: Dict[str, Node], services: Dict[str, Service],
                 ip_version: str = None, topology: str = None,
                 network_backend: str = None, cinder_backend: str = None,
                 dvr: str = None, tls_everywhere: str = None,
                 ml2_driver: str = None, ironic_inspector: str = None,
                 cleaning_network: str = None, security_group: str = None,
                 overcloud_templates: set = None, stages: List[Stage] = None,
                 test_collection: TestCollection = None):
        super().__init__({'release': release, 'infra_type': infra_type,
                          'nodes': nodes, 'services': services,
                          'ip_version': ip_version, 'topology': topology,
                          'network_backend': network_backend,
                          'cinder_backend': cinder_backend,
                          'dvr': dvr, 'tls_everywhere': tls_everywhere,
                          'ml2_driver': ml2_driver,
                          'ironic_inspector': ironic_inspector,
                          'security_group': security_group,
                          'cleaning_network': cleaning_network,
                          'overcloud_templates': overcloud_templates,
                          'test_collection': test_collection,
                          'stages': stages})

    def add_node(self, node: Node):
        """Add a node to the deployment.

        :param node: Node to add to the deployment
        :type node: Node
        """
        node_name = node.name.value
        if node_name in self.nodes:
            self.nodes[node_name].merge(node)
        else:
            self.nodes[node_name] = node

    def add_service(self, service: Service):
        """Add a service to the deployment.

        :param service: Service to add to the deployment
        :type service: Service
        """
        service_name = service.name.value
        if service_name in self.services:
            self.services[service_name].merge(service)
        else:
            self.services[service_name] = service

    def add_stage(self, stage: Stage):
        """Add a stage to the deployment.

        :param stage: Stage to add to the deployment
        :type stage: Stage
        """
        self.stages.append(stage)

    def merge(self, other):
        """Merge the information of two deployment objects representing the
        same deployment.

        :param other: The Deployment object to merge
        :type other: :class:`.Deployment`
        """
        if not self.ip_version.value:
            self.ip_version.value = other.ip_version.value
        if not self.topology.value:
            self.topology.value = other.topology.value
        if not self.network_backend.value:
            self.network_backend.value = other.network_backend.value
        if not self.cinder_backend.value:
            self.cinder_backend.value = other.cinder_backend.value
        if not self.dvr.value:
            self.dvr.value = other.dvr.value
        if not self.tls_everywhere.value:
            self.tls_everywhere.value = other.tls_everywhere.value
        if not self.ml2_driver.value:
            self.ml2_driver.value = other.ml2_driver.value
        if not self.ironic_inspector.value:
            self.ironic_inspector.value = other.ironic_inspector.value
        if not self.cleaning_network.value:
            self.cleaning_network.value = other.cleaning_network.value
        if not self.security_group.value:
            self.security_group.value = other.security_group.value

        if other.overcloud_templates.value:
            other_templates = other.overcloud_templates.value
            if self.overcloud_templates.value:
                own_templates = self.overcloud_templates.value
                all_templates = own_templates.union(other_templates)
                self.overcloud_templates.value = all_templates
            else:
                self.overcloud_templates.value = other_templates

        if other.test_collection.value:
            if self.test_collection.value:
                self.test_collection.value.merge(other.test_collection.value)
            else:
                self.test_collection.value = other.test_collection.value

        for node in other.nodes.values():
            self.add_node(node)
        for service in other.services.values():
            self.add_service(service)
        if not self.stages.value and other.stages.value:
            self.stages = other.stages
