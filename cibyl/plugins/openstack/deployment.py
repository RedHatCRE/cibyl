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
from typing import Dict

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.model import Model
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.service import Service

# pylint: disable=no-member


class Deployment(Model):
    """Openstack deployment model"""

    API = {
        'release': {
            'attr_type': str,
            'arguments': [Argument(name='--release', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Deployment release version"),
                          Argument(name='--spec', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Print complete openstack"
                                   " deployment")]
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
                                   nargs='*',
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
        'ip_version': {
            'attr_type': str,
            'arguments': [Argument(name='--ip-version', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Ip version used in the "
                                               "deployment")]
        },
        'topology': {
            'attr_type': str,
            'arguments': [Argument(name='--topology', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Topology used in the "
                                               "deployment")]
        },
        'dvr': {
            'attr_type': str,
            'arguments': [Argument(name='--dvr', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Whether dvr is used in the "
                                               "deployment")]
        },
        'tls_everywhere': {
            'attr_type': str,
            'arguments': [Argument(name='--tls-everywhere', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Whether tls-everywhere is "
                                               "used in the deployment")]
        },
        'network_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--network-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Network backend used in the "
                                               "deployment")]
        },
        'storage_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--storage-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Storage backend used in the "
                                               "deployment")]
        }
    }

    def __init__(self, release: str, infra_type: str,
                 nodes: Dict[str, Node], services: Dict[str, Service],
                 ip_version: str = None, topology: str = None,
                 network_backend: str = None, storage_backend: str = None,
                 dvr: str = None, tls_everywhere: str = None):
        super().__init__({'release': release, 'infra_type': infra_type,
                          'nodes': nodes, 'services': services,
                          'ip_version': ip_version, 'topology': topology,
                          'network_backend': network_backend,
                          'storage_backend': storage_backend,
                          'dvr': dvr, 'tls_everywhere': tls_everywhere})

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
        if not self.storage_backend.value:
            self.storage_backend.value = other.storage_backend.value
        if not self.dvr.value:
            self.dvr.value = other.dvr.value
        if not self.tls_everywhere.value:
            self.tls_everywhere.value = other.tls_everywhere.value
        for node in other.nodes.values():
            self.add_node(node)
        for service in other.services.values():
            self.add_service(service)
