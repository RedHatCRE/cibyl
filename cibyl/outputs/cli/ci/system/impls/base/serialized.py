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
import json
from abc import ABC

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.system.printer import CISystemPrinter


class SerializedBaseSystemPrinter(CISystemPrinter, ABC):
    """Default system printer for all serializer implementations.
    """

    def __init__(self,
                 load_function,
                 dump_function,
                 query=QueryType.NONE,
                 verbosity=0):
        """Constructor. See parent for more information.

        :param load_function: Function that transforms machine-readable text
            into a Python structure. Used to unmarshall output of sub-parts
            of the module.
        :type load_function: (str) -> dict
        :param dump_function: Function that transforms a Python structure into
            machine-readable text. Used to marshall the data from the
            hierarchy.
        :type dump_function: (dict) -> str
        """
        super().__init__(query, verbosity)

        self._load = load_function
        self._dump = dump_function

    @overrides
    def print_system(self, system):
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

    def print_feature(self, feature):
        """Print a feature present in a system.

        :param feature: The feature.
        :type feature: :class:`cibyl.models.ci.base.feature.Feature`
        :return: Textual representation of the provided model.
        :rtype: str
        """
        result = {
            'name': feature.name.value,
            'present': feature.present.value
        }

        return self._dump(result)


class JSONBaseSystemPrinter(SerializedBaseSystemPrinter):
    """Basic system printer that will output a system's data in JSON format.
    """

    def __init__(self,
                 query=QueryType.NONE,
                 verbosity=0,
                 indentation=4):
        """Constructor. See parent for more information.

        :param indentation: Number of spaces indenting each level of the
            JSON output.
        :type indentation: int
        """
        super().__init__(
            load_function=self._from_json,
            dump_function=self._to_json,
            query=query,
            verbosity=verbosity
        )

        self._indentation = indentation

    @property
    def indentation(self):
        """
        :return: Number of spaces preceding every level of the JSON output.
        :rtype: int
        """
        return self._indentation

    def _from_json(self, obj):
        return json.loads(obj)

    def _to_json(self, obj):
        return json.dumps(obj, indent=self._indentation)
