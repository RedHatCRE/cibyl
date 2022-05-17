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
import logging

from overrides import overrides

from cibyl.models.ci.base.system import JobsSystem
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.outputs.cli.ci.printer import CIPrinter
from cibyl.outputs.cli.ci.systems.base.colored import ColoredBaseSystemPrinter
from cibyl.outputs.cli.ci.systems.jobs.colored import ColoredJobsSystemPrinter
from cibyl.outputs.cli.ci.systems.zuul.colored import ColoredZuulSystemPrinter
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class CIColoredPrinter(ColoredPrinter, CIPrinter):
    """Prints a whole CI model hierarchy decorating the output with colors
    for easier read.
    """

    @overrides
    def print_environment(self, env):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Environment: '), 0)
        printer[0].append(env.name.value)

        for system in env.systems:
            printer.add(self._print_system(system), 1)

        return printer.build()

    def _print_system(self, system):
        """
        :param system: The system.
        :type system: :class:`cibyl.models.ci.base.system.System`
        :return: Textual representation of the system.
        :rtype: str
        """

        def get_printer():
            # Check specialized printers
            if isinstance(system, ZuulSystem):
                return ColoredZuulSystemPrinter(
                    self.query, self.verbosity, self.palette
                )

            if isinstance(system, JobsSystem):
                return ColoredJobsSystemPrinter(
                    self.query, self.verbosity, self.palette
                )

            LOG.warning(
                'Custom printer not found for system of type: %s. '
                'Continuing with default printer...',
                type(system)
            )

            # Go with the default printer
            return ColoredBaseSystemPrinter(
                self.query, self.verbosity, self.palette
            )

        return get_printer().print_system(system)
