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
from typing import Optional

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.models.ci.base.system import System
from cibyl.models.product.feature import Feature
from cibyl.outputs.cli.ci.system.common.features import is_features_query
from cibyl.outputs.cli.ci.system.printer import CISystemPrinter
from cibyl.outputs.cli.printer import JSON, PROV, STDJSON, SerializedPrinter


class SerializedBaseSystemPrinter(
    SerializedPrinter[PROV],
    CISystemPrinter,
    ABC
):
    """Default system printer for all serializer implementations.
    """

    @overrides
    def print_system(self, system: System) -> str:
        result = {
            'name': system.name.value,
            'type': system.system_type.value
        }

        if is_features_query(self.query):
            result['features'] = []

            for feature in system.features.values():
                result['features'].append(
                    self.provider.load(
                        self.print_feature(feature)
                    )
                )

        return self.provider.dump(result)

    def print_feature(self, feature: Feature) -> str:
        result = {
            'name': feature.name.value,
            'present': feature.present.value
        }

        return self.provider.dump(result)


class JSONBaseSystemPrinter(SerializedBaseSystemPrinter[JSON]):
    """Basic system printer that will output a system's data in JSON format.
    """

    def __init__(
        self,
        provider: Optional[JSON] = None,
        query: QueryType = QueryType.NONE,
        verbosity: int = 0
    ):
        """Constructor. See parent for more information.

        :param provider: Implementation of a JSON marshaller / unmarshaller.
            Leave as 'None' to let this build its own.
        """
        if provider is None:
            provider = STDJSON()

        super().__init__(provider, query, verbosity)
