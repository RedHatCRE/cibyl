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
from cibyl.outputs.cli.ci.system.common.stages import print_stage
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.plugins.openstack.storage import Storage
from cibyl.utils.strings import IndentedTextBuilder


class OSColoredPrinter(ColoredPrinter, OSPrinter):
    """Provides a human-readable representation of OS models decorated with
    coloring for easier readability.
    """

    def _print_deployment_network_section(self, network: Network,
                                          printer: IndentedTextBuilder):
        """Print the network related properties of the deployment.
        :param network: Network properties of an Openstack deployment
        :param printer: Printer that provides the output representation
        :returns: Whether the network section of the deployment is empty
        """
        is_empty_network = True
        printer.add(self.palette.blue("Network: "), 1)
        ip_version = network.ip_version.value
        if ip_version and ip_version != "unknown":
            is_empty_network = False
            printer.add(self.palette.blue('IP version: '), 2)
            printer[-1].append(network.ip_version)

        if network.network_backend.value:
            if network.network_backend.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('Network backend: '), 2)
                printer[-1].append(network.network_backend)

        if network.ml2_driver.value:
            if network.ml2_driver.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('ML2 driver: '), 2)
                printer[-1].append(network.ml2_driver)

        if network.security_group.value:
            if network.security_group.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('Security group mechanism: '),
                            2)
                printer[-1].append(network.security_group)

        if network.dvr.value:
            if network.dvr.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('DVR: '), 2)
                printer[-1].append(network.dvr)

        if network.tls_everywhere.value:
            if network.tls_everywhere.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('TLS everywhere: '), 2)
                printer[-1].append(network.tls_everywhere)

        if is_empty_network:
            printer.pop()
        return is_empty_network

    def _print_deployment_storage_section(self, storage: Storage,
                                          printer: IndentedTextBuilder
                                          ) -> bool:
        """Print the storage related properties of the storage.
        :param storage: Storage properties of an Openstack deployment
        :param printer: Printer that provides the output representation
        :returns: Whether the network section of the storage is empty
        """
        is_empty_storage = True
        printer.add(self.palette.blue("Storage: "), 1)

        if storage.cinder_backend.value:
            if storage.cinder_backend.value != "N/A" or self.verbosity > 0:
                is_empty_storage = False
                printer.add(self.palette.blue('Cinder backend: '), 2)
                printer[-1].append(storage.cinder_backend)

        if is_empty_storage:
            printer.pop()
        return is_empty_storage

    def _print_deployment_ironic_section(self, ironic: Ironic,
                                         printer: IndentedTextBuilder) -> bool:
        """Print the ironic related properties of the deployment.
        :param ironic: Ironic-related properties of an Openstack
        deployment
        :param printer: Printer that provides the output representation
        :returns: Whether the network section of the deployment is empty
        """
        is_empty_ironic = True
        printer.add(self.palette.blue("Ironic: "), 1)

        if ironic.ironic_inspector.value:
            if ironic.ironic_inspector.value != "N/A" or \
               self.verbosity > 0:
                is_empty_ironic = False
                printer.add(self.palette.blue('Ironic inspector: '), 2)
                printer[-1].append(ironic.ironic_inspector)

        if ironic.cleaning_network.value:
            if ironic.cleaning_network.value != "N/A" or \
               self.verbosity > 0:
                is_empty_ironic = False
                printer.add(self.palette.blue('Cleaning network: '), 2)
                printer[-1].append(ironic.cleaning_network)

        if is_empty_ironic:
            printer.pop()
        return is_empty_ironic

    def print_deployment(self, deployment):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Openstack deployment: '), 0)
        is_empty_deployment = True

        if deployment.release.value:
            if self.verbosity > 0 or deployment.release.value != "N/A":
                is_empty_deployment = False
                printer.add(self.palette.blue('Release: '), 1)
                printer[-1].append(deployment.release.value)

        if deployment.infra_type.value:
            if self.verbosity > 0 or deployment.infra_type.value != "N/A":
                is_empty_deployment = False
                printer.add(self.palette.blue('Infra type: '), 1)
                printer[-1].append(deployment.infra_type)

        if deployment.topology.value:
            if self.verbosity > 0 or deployment.topology.value != "N/A":
                is_empty_deployment = False
                printer.add(self.palette.blue('Topology: '), 1)
                printer[-1].append(deployment.topology)

        is_empty_network = True
        if deployment.network.value:
            network = deployment.network.value
            is_empty_network = self._print_deployment_network_section(network,
                                                                      printer)
        is_empty_storage = True
        if deployment.storage.value:
            storage = deployment.storage.value
            is_empty_storage = self._print_deployment_storage_section(storage,
                                                                      printer)
        is_empty_ironic = True
        if deployment.ironic.value:
            ironic = deployment.ironic.value
            is_empty_ironic = self._print_deployment_ironic_section(ironic,
                                                                    printer)
        if deployment.overcloud_templates.value:
            if deployment.overcloud_templates.value != "N/A" or \
               self.verbosity > 0:
                is_empty_deployment = False
                printer.add(self.palette.blue('Overcloud templates: '), 1)
                if isinstance(deployment.overcloud_templates.value, str):
                    printer[-1].append(deployment.overcloud_templates.value)
                else:
                    templates = deployment.overcloud_templates.value
                    for template in sorted(templates):
                        printer.add(self.palette.blue('- '), 2)
                        printer[-1].append(template)

        if deployment.test_collection.value:
            if deployment.test_collection.value != "N/A" or \
               self.verbosity > 0:
                is_empty_deployment = False
                if isinstance(deployment.test_collection.value, str):
                    printer.add(self.palette.blue('Testing information: '), 1)
                    printer[-1].append(deployment.test_collection.value)
                else:
                    testing_string = self.print_test_collection(
                            deployment.test_collection.value)
                    if testing_string:
                        printer.add(testing_string, 1)
                    elif self.verbosity > 0:
                        # if testing collection was empty but verbose output
                        # was request, we still want to print the field
                        printer.add(self.palette.blue('Testing information: '),
                                    1)
                        printer[-1].append('N/A')

        is_empty_deployment &= (is_empty_network and is_empty_storage and
                                is_empty_ironic)

        if deployment.nodes.values():
            is_empty_deployment = False
            printer.add(self.palette.blue('Nodes: '), 1)
            for node in deployment.nodes.values():
                printer.add(self.print_node(node), 2)

        for service in deployment.services.values():
            is_empty_deployment = False
            printer.add(self.print_service(service), 1)

        if deployment.stages.value:
            is_empty_deployment = False
            printer.add(self.palette.blue('Stages: '), 1)
            for stage in deployment.stages:
                printer.add(print_stage(stage, self.palette,
                                        self.verbosity), 2)

        if is_empty_deployment:
            # remove the "Openstack deployment" line
            printer.pop()
            printer.add("No openstack information associated with this job", 1)
        return printer.build()

    def print_test_collection(self, test_collection):
        """Print the test collection used in an Openstack deployment.

        :param test_collection: The test collection used in the deployment
        :type test_collection: :class:`TestCollection`
        """
        has_testing_info = False
        printer = IndentedTextBuilder()
        printer.add(self.palette.blue('Testing information: '), 0)
        if test_collection.tests.value:
            has_testing_info = True
            printer.add(self.palette.blue('Test suites: '), 1)
            for test in sorted(test_collection.tests.value):
                printer.add(self.palette.blue('- '), 2)
                printer[-1].append(test)

        if test_collection.setup.value:
            has_testing_info = True
            printer.add(self.palette.blue('Setup: '), 1)
            printer[-1].append(test_collection.setup.value)
        if not has_testing_info:
            # if the test_collection object had nothing, remove the header
            printer.pop()
        return printer.build()

    def print_node(self, node):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('- '), 0)
        printer[-1].append(node.name.value)

        if self.verbosity > 0:
            if node.role.value:
                printer.add(self.palette.blue('Role: '), 1)
                printer[-1].append(node.role)

        if node.containers.value:
            for container in node.containers.values():
                printer.add(self.print_container(container), 1)

        if node.packages.value:
            for package in node.packages.values():
                printer.add(self.print_package(package), 1)

        return printer.build()

    def print_package(self, package):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Package: '), 0)
        printer[-1].append(package.name)

        if package.origin.value:
            printer.add(self.palette.blue('Origin: '), 1)
            printer[-1].append(package.origin)

        return printer.build()

    def print_service(self, service):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Service name: '), 0)
        printer[-1].append(service.name.value)

        if self.verbosity > 0:
            if service.configuration.value:
                for parameter, value in service.configuration.value.items():
                    printer.add(self.palette.blue(f'{parameter}: '), 1)
                    printer[-1].append(value)

        return printer.build()

    def print_container(self, container):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Container: '), 0)
        printer[-1].append(container.name)

        if container.image.value:
            printer.add(self.palette.blue('Image: '), 1)
            printer[-1].append(container.image)

        if container.packages.value:
            for package in container.packages.values():
                printer.add(self.print_package(package), 1)

        return printer.build()
