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

from cibyl.outputs.cli.ci.system.impls.base.colored import \
    ColoredBaseSystemPrinter
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColoredGithubActionsSystemPrinter(ColoredBaseSystemPrinter):
    """Printer meant for :class:`WorkflowsSystem`, decorated with colors for
    easier read.
    """

    @overrides
    def print_system(self, system):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), 0)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        for workflow in system.workflows.values():
            printer.add(self.print_workflow(workflow), 1)

        if system.is_queried():
            header = 'Total workflows found in query: '

            printer.add(self._palette.blue(header), 1)
            printer[-1].append(len(system.workflows))
        else:
            printer.add(self._palette.blue('No query performed'), 1)

        return printer.build()

    def print_workflow(self, workflow):
        """
        :param workflow: The workflow.
        :type workflow:
            :class:`cibyl.models.ci.github_actions.workflow.Workflow`
        :return: Textual representation of the provided model.
        :rtype: str
        """
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Workflow: '), 0)
        printer[-1].append(workflow.name.value)

        if self.verbosity > 0:
            if workflow.url.value:
                printer.add(self._palette.blue('URL: '), 1)
                printer[-1].append(workflow.url.value)

        return printer.build()
