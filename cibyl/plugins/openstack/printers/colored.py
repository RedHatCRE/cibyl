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

    def print_deployment(self, deployment):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Openstack deployment: '), 0)
        is_empty_deployment = True

        if deployment.release.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('Release: '), 1)
            printer[-1].append(deployment.release.value)

        if deployment.infra_type.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('Infra type: '), 1)
            printer[-1].append(deployment.infra_type)

        if deployment.topology.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('Topology: '), 1)
            printer[-1].append(deployment.topology)

        ip_version = deployment.ip_version.value
        if ip_version and ip_version != "unknown":
            is_empty_deployment = False
            printer.add(self._palette.blue('IP version: '), 1)
            printer[-1].append(deployment.ip_version)

        if deployment.network_backend.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('Network backend: '), 1)
            printer[-1].append(deployment.network_backend)

        if deployment.dvr.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('DVR: '), 1)
            printer[-1].append(deployment.dvr)

        if deployment.ml2_driver.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('ML2 driver: '), 1)
            printer[-1].append(deployment.ml2_driver)

        if deployment.tls_everywhere.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('TLS everywhere: '), 1)
            printer[-1].append(deployment.tls_everywhere)

        if deployment.storage_backend.value:
            is_empty_deployment = False
            printer.add(self._palette.blue('Storage backend: '), 1)
            printer[-1].append(deployment.storage_backend)

        if deployment.nodes.values():
            is_empty_deployment = False
            printer.add(self._palette.blue('Nodes: '), 1)
            for node in deployment.nodes.values():
                printer.add(self.print_node(node), 2)

        for service in deployment.services.values():
            is_empty_deployment = False
            printer.add(self.print_service(service), 1)

        if is_empty_deployment:
            # remove the "Openstack deployment" line
            printer.pop()
            printer.add("No openstack information associated with this job", 1)
        return printer.build()

    def print_node(self, node):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('- '), 0)
        printer[-1].append(node.name.value)

        if self.verbosity > 0:
            if node.role.value:
                printer.add(self._palette.blue('Role: '), 1)
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

        printer.add(self._palette.blue('Package: '), 0)
        printer[-1].append(package.name)

        if package.origin.value:
            printer.add(self._palette.blue('Origin: '), 1)
            printer[-1].append(package.origin)

        return printer.build()

    def print_service(self, service):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Service name: '), 0)
        printer[-1].append(service.name.value)

        if self.verbosity > 0:
            if service.configuration.value:
                for parameter, value in service.configuration.value.items():
                    printer.add(self._palette.blue(f'{parameter}: '), 1)
                    printer[-1].append(value)

        return printer.build()

    def print_container(self, container):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Container: '), 0)
        printer[-1].append(container.name)

        if container.image.value:
            printer.add(self._palette.blue('Image: '), 1)
            printer[-1].append(container.image)

        if container.packages.value:
            for package in container.packages.values():
                printer.add(self.print_package(package), 1)

        return printer.build()
