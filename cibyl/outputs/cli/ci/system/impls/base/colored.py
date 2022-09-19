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
from cibyl.models.ci.base.system import System
from cibyl.models.product.feature import Feature
from cibyl.outputs.cli.ci.system.common.features import is_features_query
from cibyl.outputs.cli.ci.system.printer import CISystemPrinter
from cibyl.outputs.cli.ci.system.utils.sorting.builds import SortBuildsByUUID
from cibyl.outputs.cli.ci.system.utils.sorting.jobs import SortJobsByName
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.colors import ColorPalette, DefaultPalette
from cibyl.utils.sorting import BubbleSortAlgorithm, SortingAlgorithm
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColoredBaseSystemPrinter(ColoredPrinter, CISystemPrinter):
    """Default printer for all system models. This one is decorated with
    colors for easier read.
    """

    def __init__(self,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0,
                 palette: ColorPalette = DefaultPalette(),
                 job_sorter: SortingAlgorithm
                 = BubbleSortAlgorithm(SortJobsByName()),
                 build_sorter: SortingAlgorithm
                 = BubbleSortAlgorithm(SortBuildsByUUID())):
        """Constructor. See parent for more information.

        :param job_sorter: Determines the order on which jobs are printed.
        :param build_sorter: Determines the order on which builds are printed.
        """
        super().__init__(query, verbosity, palette)

        self._job_sorter = job_sorter
        self._build_sorter = build_sorter

    @overrides
    def print_system(self, system: System) -> str:
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), 0)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        if is_features_query(self.query):
            for feature in system.features.values():
                printer.add(self.print_feature(feature), 1)

        return printer.build()

    def print_feature(self, feature: Feature) -> str:
        printer = IndentedTextBuilder()
        name = feature.name.value
        present = feature.present.value
        printer.add(self.palette.blue(f'{name} feature: '), 0)
        printer[-1].append(present)
        return printer.build()
