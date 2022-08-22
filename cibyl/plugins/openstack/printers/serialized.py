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

from overrides import overrides

from cibyl.outputs.cli.printer import JSONPrinter, SerializedPrinter
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.plugins.openstack.service import Service


class OSSerializedPrinter(OSPrinter, SerializedPrinter, ABC):
    """Provides a machine-readable representation of the plugin's models for
    easy readability from a machine.
    """

    @overrides
    def print_deployment(self, deployment: Deployment) -> str:
        result = {
            'release': deployment.release.value,
            'infra_type': deployment.infra_type.value,
            'topology': deployment.topology.value
        }

        return self.provider.dump(result)

    @overrides
    def print_node(self, node: Node) -> str:
        pass

    @overrides
    def print_container(self, container: Container) -> str:
        pass

    @overrides
    def print_package(self, package: Package) -> str:
        pass

    @overrides
    def print_service(self, service: Service) -> str:
        pass


class OSJSONPrinter(JSONPrinter, OSSerializedPrinter):
    """Provides a representation of the plugin's models in JSON format.
    """
