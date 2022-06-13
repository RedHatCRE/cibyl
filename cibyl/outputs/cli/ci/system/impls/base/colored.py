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

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.system.printer import CISystemPrinter
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColoredBaseSystemPrinter(ColoredPrinter, CISystemPrinter):
    """Default printer for all system models. This one is decorated with
    colors for easier read.
    """

    @overrides
    def print_system(self, system, indent=0):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), indent)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        if self.query in (QueryType.FEATURES_JOBS, QueryType.FEATURES):
            for feature in system.features.values():
                printer.add(self.print_feature(feature), 1)

        return printer.build()

    def print_feature(self, feature):
        """Print a feature present in a system.
        :param feature: The feature.
        :type feature: :class:`cibyl.models.ci.base.feature.Feature`
        :return: Textual representation of the provided model.
        :rtype: str
        """
        printer = IndentedTextBuilder()
        name = feature.name.value
        present = feature.present.value
        printer.add(self.palette.blue(f'{name} feature: '), 0)
        printer[-1].append(present)
        return printer.build()
