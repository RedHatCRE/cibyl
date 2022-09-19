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
from abc import ABC
from typing import Optional, Union

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.printer import JSON, PROV, STDJSON, SerializedPrinter
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.test_collection import TestCollection


class OSSerializedPrinter(SerializedPrinter[PROV], OSPrinter, ABC):
    """Provides a machine-readable representation of the plugin's models for
    easy readability from a machine.
    """

    @overrides
    def print_deployment(self, deployment: Deployment) -> str:
        network = deployment.network.value
        storage = deployment.storage.value
        ironic = deployment.ironic.value

        result = {
            'release': deployment.release.value,
            'infra_type': deployment.infra_type.value,
            'topology': deployment.topology.value,
            'network': {
                'ip_version': network.ip_version.value,
                'network_backend': network.network_backend.value,
                'ml2_driver': network.ml2_driver.value,
                'security_group': network.security_group.value,
                "dvr": network.dvr.value,
                'tls_everywhere': network.tls_everywhere.value
            } if network else {},
            'storage': {
                'cinder_backend': storage.cinder_backend.value
            } if storage else {},
            'ironic': {
                'ironic_inspector': ironic.ironic_inspector.value,
                'cleaning_network': ironic.cleaning_network.value
            } if ironic else {},
            'overcloud_templates':
                self._print_overcloud_templates(
                    deployment.overcloud_templates.value
                )
                if deployment.overcloud_templates.value else [],
            'test_collection':
                self.provider.load(
                    self.print_test_collection(
                        deployment.test_collection.value
                    )
                )
                if deployment.test_collection.value else {},
            'nodes': [
                self.provider.load(self.print_node(node))
                for node in deployment.nodes.values()
            ],
            'services': [
                self.provider.load(self.print_service(service))
                for service in deployment.services.values()
            ],
            'stages': [
                {
                    'name': stage.name.value,
                    'status': stage.status.value,
                    'duration': stage.duration.value
                }
                for stage in deployment.stages
            ]
        }

        return self.provider.dump(result)

    @overrides
    def print_test_collection(self, collection: TestCollection) -> str:
        if isinstance(collection, str):
            # sometime the test collection is stored as a string indicating
            # that no test information was available (usually N/A), so in those
            # cases we'll replace the collection with an empty one
            collection = TestCollection()

        result = {
            # sort list of tests so it's consistently displayed
            'tests':
                sorted(list(collection.tests.value))
                if collection.tests.value else [],
            'setup': collection.setup.value
        }

        return self.provider.dump(result)

    @overrides
    def print_node(self, node: Node) -> str:
        result = {
            'role': node.role.value,
            'containers': [
                self.provider.load(self.print_container(container))
                for container in node.containers.values()
            ],
            'packages': [
                self.provider.load(self.print_package(package))
                for package in node.packages.values()
            ]
        }

        return self.provider.dump(result)

    @overrides
    def print_container(self, container: Container) -> str:
        result = {
            'name': container.name.value,
            'image': container.image.value,
            'packages': [
                self.provider.load(self.print_package(package))
                for package in container.packages.values()
            ]
        }

        return self.provider.dump(result)

    @overrides
    def print_package(self, package: Package) -> str:
        result = {
            'name': package.name.value,
            'origin': package.origin.value
        }

        return self.provider.dump(result)

    @overrides
    def print_service(self, service: Service) -> str:
        result = {
            'name': service.name.value,
            'configuration': service.configuration.value
        }

        return self.provider.dump(result)

    def _print_overcloud_templates(self, templates: Union[str, set]) -> list:
        if isinstance(templates, str):
            # sometimes the test collection is stored as a string indicating
            # that no test information was available (usually N/A), so in those
            # cases we'll replace the collection with an empty one
            return []
        return list(templates)


class OSJSONPrinter(OSSerializedPrinter[JSON]):
    """Provides a representation of the plugin's models in JSON format.
    """

    def __init__(
        self,
        provider: Optional[JSON],
        query: QueryType = QueryType.NONE,
        verbosity: int = 0
    ):
        """Constructor. See parent for more information.

        :param provider: Implementation of a JSON marshaller / unmarshaller.
            Leave as 'None' to let this build its own.
        """
        if provider is None:
            provider = STDJSON()

        super().__init__(provider, query, verbosity)
