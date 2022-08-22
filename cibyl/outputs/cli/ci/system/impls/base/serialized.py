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
from typing import Callable

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.models.ci.base.system import System
from cibyl.models.product.feature import Feature
from cibyl.outputs.cli.ci.system.printer import CISystemPrinter
from cibyl.outputs.cli.printer import SerializedPrinter, JSONPrinter


class SerializedBaseSystemPrinter(CISystemPrinter, SerializedPrinter, ABC):
    """Default system printer for all serializer implementations.
    """

    def __init__(self,
                 load_function: Callable[[str], dict],
                 dump_function: Callable[[dict], str],
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0):
        """Constructor. See parent for more information.

        :param load_function: Function that transforms machine-readable text
            into a Python structure. Used to unmarshall output of sub-parts
            of the module.
        :param dump_function: Function that transforms a Python structure into
            machine-readable text. Used to marshall the data from the
            hierarchy.
        """
        super().__init__(query, verbosity)

        self._load = load_function
        self._dump = dump_function

    @overrides
    def print_system(self, system: System) -> str:
        result = {
            'name': system.name.value,
            'type': system.system_type.value
        }

        if self.query in (QueryType.FEATURES_JOBS, QueryType.FEATURES):
            result['features'] = []

            for feature in system.features.values():
                result['features'].append(
                    self._load(
                        self.print_feature(feature)
                    )
                )

        return self._dump(result)

    def print_feature(self, feature: Feature) -> str:
        """Print a feature present in a system.

        :param feature: The feature.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': feature.name.value,
            'present': feature.present.value
        }

        return self._dump(result)


class JSONBaseSystemPrinter(JSONPrinter, SerializedBaseSystemPrinter):
    """Basic system printer that will output a system's data in JSON format.
    """
