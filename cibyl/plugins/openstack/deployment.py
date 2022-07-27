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
from typing import Dict, List, Optional, Set

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.stage import Stage
from cibyl.models.model import Model
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection

# pylint: disable=no-member


class Deployment(Model):
    """Openstack deployment model.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    API = {
        'release': {
            'attr_type': str,
            'arguments': [Argument(name='--release', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Deployment release version"),
                          ]
        },
        'infra_type': {
            'attr_type': str,
            'arguments': [Argument(name='--infra-type', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Infra type")]
        },
        'nodes': {
            'attr_type': Node,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--nodes', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Nodes on the deployment"),
                          Argument(name='--controllers', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   ranged=True,
                                   description="Number of controllers used "
                                               "in the deployment"),
                          Argument(name='--computes', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   ranged=True,
                                   description="Number of computes used "
                                               "in the deployment")]
        },
        'services': {
            'attr_type': Service,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--services', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Services in the deployment")]
        },
        'topology': {
            'attr_type': str,
            'arguments': [Argument(name='--topology', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Topology used in the "
                                               "deployment")]
        },
        'network': {
            'attr_type': Network,
            'arguments': []
        },

        'ironic': {
            'attr_type': Ironic,
            'arguments': []
        },
        'overcloud_templates': {
            'arguments': [Argument(name='--overcloud-templates', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="TripleO templates use in the "
                                               "deployment")]
        },
        'test_collection': {
            'attr_type': TestCollection,
            'arguments': [Argument(name="--test-setup", arg_type=str,
                                   func='get_deployment', nargs=1,
                                   choices=('rpm', 'git'),
                                   description="Source for the test setup")]
        },
        'storage': {
            'attr_type': Storage,
            'arguments': []
        },
        'stages': {
            'attr_type': Stage,
            'attribute_value_class': AttributeListValue,
            'arguments': []
            }
    }

    def __init__(self,
                 release: Optional[str] = None,
                 infra_type: Optional[str] = None,
                 nodes: Optional[Dict[str, Node]] = None,
                 services: Optional[Dict[str, Service]] = None,
                 topology: Optional[str] = None,
                 network: Optional[Network] = None,
                 storage: Optional[Storage] = None,
                 ironic: Optional[Ironic] = None,
                 overcloud_templates: Optional[Set[str]] = None, stages:
                 Optional[List[Stage]] = None,
                 test_collection: Optional[TestCollection] = None):
        super().__init__({'release': release, 'infra_type': infra_type,
                          'nodes': nodes, 'services': services,
                          'topology': topology, 'network': network,
                          'storage': storage, 'ironic': ironic,
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
        if not self.topology.value:
            self.topology.value = other.topology.value

        if other.network.value:
            if self.network.value:
                self.network.value.merge(other.network.value)
            else:
                self.network = other.network

        if other.storage.value:
            if self.storage.value:
                self.storage.value.merge(other.storage.value)
            else:
                self.storage = other.storage

        if other.ironic.value:
            if self.ironic.value:
                self.ironic.value.merge(other.ironic.value)
            else:
                self.ironic = other.ironic

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
