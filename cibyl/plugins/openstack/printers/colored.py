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
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.publisher import PrintMode
from cibyl.utils.colors import DefaultPalette
from cibyl.utils.strings import IndentedTextBuilder


class ColoredPrinter(OSPrinter):
    def __init__(self,
                 mode=PrintMode.COMPLETE, verbosity=0,
                 palette=DefaultPalette()):
        super().__init__(mode, verbosity)

        self._palette = palette

    @property
    def palette(self):
        return self._palette

    def print_container(self, container):
        raise NotImplementedError

    def print_deployment(self, deployment):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Release: '), 0)
        printer[-1].append(deployment.release.value)

        if deployment.infra_type.value:
            printer.add(self._palette.blue('Infra type: '), 1)
            printer[-1].append(deployment.infra_type)

        if deployment.ip_version.value:
            printer.add(self._palette.blue('IP version: '), 1)
            printer[-1].append(deployment.ip_version)

        if deployment.topology.value:
            printer.add(self._palette.blue('Topology: '), 1)
            printer[-1].append(deployment.topology)

        if deployment.network_backend.value:
            printer.add(self._palette.blue('Network backend: '), 1)
            printer[-1].append(deployment.network_backend)

        if deployment.storage_backend.value:
            printer.add(self._palette.blue('Storage backend: '), 1)
            printer[-1].append(deployment.storage_backend)

        if deployment.dvr.value:
            printer.add(self._palette.blue('DVR: '), 1)
            printer[-1].append(deployment.dvr)

        if deployment.tls_everywhere.value:
            printer.add(self._palette.blue('TLS everywhere: '), 1)
            printer[-1].append(deployment.tls_everywhere)

        for node in deployment.nodes.values():
            printer.add(self.print_node(node), 1)

        for service in deployment.services.values():
            printer.add(self.print_service(service), 1)

        return printer.build()

    def print_node(self, node):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Node name: '), 0)
        printer[-1].append(node.name.value)

        if self.verbosity > 0:
            if node.role.value:
                printer.add(self._palette.blue('Role: '), 1)
                printer[-1].append(node.role)

        if node.containers.value:
            for container in node.containers:
                printer.add(self._palette.blue('Container: '), 1)
                printer[-1].append(self.print_container(container))

        if node.packages.value:
            for package in node.packages:
                printer.add(self._palette.blue('Package: '), 1)
                printer[-1].append(self.print_package(package), 1)

        return printer.build()

    def print_package(self, package):
        raise NotImplementedError

    def print_service(self, service):
        printer = IndentedTextBuilder()

        printer.add('Service name: ', 0)
        printer[-1].append(service.name.value)

        if self.verbosity > 0:
            if service.configuration.value:
                for parameter, value in service.configuration.value.items():
                    printer.add(self._palette.blue(f'{parameter}: '), 1)
                    printer[-1].append(value)

        return printer.build()
