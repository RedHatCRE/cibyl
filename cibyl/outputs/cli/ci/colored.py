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
from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.printer import CIPrinter
from cibyl.outputs.cli.ci.systems.factory import ColoredSystemPrinterFactory
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.colors import DefaultPalette
from cibyl.utils.strings import IndentedTextBuilder


class CIColoredPrinter(CIPrinter, ColoredPrinter):
    def __init__(self,
                 query=QueryType.NONE,
                 verbosity=0,
                 palette=DefaultPalette(),
                 system_printer_factory=None):
        super().__init__(query, verbosity, palette)

        if not system_printer_factory:
            system_printer_factory = ColoredSystemPrinterFactory(self)

        self._system_printer_factory = system_printer_factory

    @overrides
    def print_environment(self, env):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Environment: '), 0)
        printer[0].append(env.name.value)

        for system in env.systems:
            system_printer = self._system_printer_factory.from_system(system)

            printer.add(system_printer.print_system(system), 1)

        return printer.build()
