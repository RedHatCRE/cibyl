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
from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.system.common.stages import print_stage
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.utils.colors import DefaultPalette
from cibyl.utils.strings import IndentedTextBuilder


class OSColoredPrinter(OSPrinter):
    """Provides a human-readable representation of OS models decorated with
    coloring for easier readability.
    """

    def __init__(self,
                 query=QueryType.NONE, verbosity=0,
                 palette=DefaultPalette()):
        """Constructor.

        See parents for more information.

        :param palette: Palette of colors to be used.
        :type palette: :class:`cibyl.utils.colors.ColorPalette`
        """
        super().__init__(query, verbosity)

        self._palette = palette

    @property
    def palette(self):
        """
        :return: The palette currently in use.
        :rtype: :class:`cibyl.utils.colors.ColorPalette`
        """
        return self._palette

    def _print_deployment_network_section(self, deployment, printer):
        """Print the network related properties of the deployment.
        :param deployment: Deployment model representing an Openstack
        deployment
        :type deployment: :class:`cibyl.plugins.openstack.deployment`
        :param printer: Printer that provides the output representation
        :type printer: :class:`cibyl.utils.strings.IndentedTextBuilder`
        :returns: Whether the network section of the deployment is empty
        """
        is_empty_network = True
        printer.add(self.palette.blue("Network: "), 1)
        ip_version = deployment.ip_version.value
        if ip_version and ip_version != "unknown":
            is_empty_network = False
            printer.add(self.palette.blue('IP version: '), 2)
            printer[-1].append(deployment.ip_version)

        if deployment.network_backend.value:
            is_empty_network = False
            printer.add(self.palette.blue('Network backend: '), 2)
            printer[-1].append(deployment.network_backend)

        if deployment.ml2_driver.value:
            if deployment.ml2_driver.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('ML2 driver: '), 2)
                printer[-1].append(deployment.ml2_driver)

        if deployment.security_group.value:
            if deployment.security_group.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('Security group mechanism: '),
                            2)
                printer[-1].append(deployment.security_group)

        if deployment.dvr.value:
            if deployment.dvr.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('DVR: '), 2)
                printer[-1].append(deployment.dvr)

        if deployment.tls_everywhere.value:
            if deployment.tls_everywhere.value != "N/A" or self.verbosity > 0:
                is_empty_network = False
                printer.add(self.palette.blue('TLS everywhere: '), 2)
                printer[-1].append(deployment.tls_everywhere)

        if is_empty_network:
            printer.pop()
        return is_empty_network

    def _print_deployment_storage_section(self, deployment, printer):
        """Print the storage related properties of the deployment.
        :param deployment: Deployment model representing an Openstack
        deployment
        :type deployment: :class:`cibyl.plugins.openstack.deployment`
        :param printer: Printer that provides the output representation
        :type printer: :class:`cibyl.utils.strings.IndentedTextBuilder`
        :returns: Whether the network section of the deployment is empty
        """
        is_empty_storage = True
        printer.add(self.palette.blue("Storage: "), 1)

        if deployment.cinder_backend.value:
            if deployment.cinder_backend.value != "N/A" or self.verbosity > 0:
                is_empty_storage = False
                printer.add(self.palette.blue('Cinder backend: '), 2)
                printer[-1].append(deployment.cinder_backend)

        if is_empty_storage:
            printer.pop()
        return is_empty_storage

    def _print_deployment_ironic_section(self, deployment, printer):
        """Print the ironic related properties of the deployment.
        :param deployment: Deployment model representing an Openstack
        deployment
        :type deployment: :class:`cibyl.plugins.openstack.deployment`
        :param printer: Printer that provides the output representation
        :type printer: :class:`cibyl.utils.strings.IndentedTextBuilder`
        :returns: Whether the network section of the deployment is empty
        """
        is_empty_ironic = True
        printer.add(self.palette.blue("Ironic: "), 1)

        if deployment.ironic_inspector.value:
            if deployment.ironic_inspector.value != "N/A" or \
               self.verbosity > 0:
                is_empty_ironic = False
                printer.add(self.palette.blue('Ironic inspector: '), 2)
                printer[-1].append(deployment.ironic_inspector)

        if deployment.cleaning_network.value:
            if deployment.cleaning_network.value != "N/A" or \
               self.verbosity > 0:
                is_empty_ironic = False
                printer.add(self.palette.blue('Cleaning network: '), 2)
                printer[-1].append(deployment.cleaning_network)

        if is_empty_ironic:
            printer.pop()
        return is_empty_ironic

    def print_deployment(self, deployment):
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Openstack deployment: '), 0)
        is_empty_deployment = True

        if deployment.release.value:
            is_empty_deployment = False
            printer.add(self.palette.blue('Release: '), 1)
            printer[-1].append(deployment.release.value)

        if deployment.infra_type.value:
            is_empty_deployment = False
            printer.add(self.palette.blue('Infra type: '), 1)
            printer[-1].append(deployment.infra_type)

        if deployment.topology.value:
            is_empty_deployment = False
            printer.add(self.palette.blue('Topology: '), 1)
            printer[-1].append(deployment.topology)

        is_empty_network = self._print_deployment_network_section(deployment,
                                                                  printer)
        is_empty_storage = self._print_deployment_storage_section(deployment,
                                                                  printer)
        is_empty_ironic = self._print_deployment_ironic_section(deployment,
                                                                printer)
        if deployment.overcloud_templates.value:
            if deployment.overcloud_templates.value != "N/A" or \
               self.verbosity > 0:
                is_empty_deployment = False
                printer.add(self.palette.blue('Overcloud templates: '), 1)
                if isinstance(deployment.overcloud_templates.value, str):
                    printer[-1].append(deployment.overcloud_templates.value)
                else:
                    for template in deployment.overcloud_templates.value:
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
                    printer.add(self.print_test_collection(
                                    deployment.test_collection.value), 1)

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
        printer = IndentedTextBuilder()
        printer.add(self.palette.blue('Testing information: '), 0)
        printer.add(self.palette.blue('Test suites: '), 1)
        if test_collection.tests.value:
            for test in test_collection.tests.value:
                printer.add(self.palette.blue('- '), 2)
                printer[-1].append(test)

        if test_collection.setup.value:
            printer.add(self.palette.blue('Setup: '), 1)
            printer[-1].append(test_collection.setup.value)
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
