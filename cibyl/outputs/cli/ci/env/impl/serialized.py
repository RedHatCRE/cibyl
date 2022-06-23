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
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.colors import DefaultPalette


class SerializedDataPrinter(ColoredPrinter, CIPrinter, ABC):
    def __init__(self,
                 load_function,
                 dump_function,
                 query=QueryType.NONE,
                 verbosity=0,
                 palette=DefaultPalette()):
        """Constructor. See parent for more information.

        :param load_function:
        :type load_function: (str) -> dict
        :param dump_function:
        :type dump_function: (dict) -> str
        """
        super().__init__(query, verbosity, palette)

        self._load = load_function
        self._dump = dump_function

    @overrides
    def print_environment(self, env):
        def get_systems():
            systems = {}

            for system in env.systems:
                key = system.name.value
                systems[key] = self._load(self._print_system(system))

            return systems

        result = {
            'name': env.name.value,
            'systems': get_systems()
        }

        return self._dump(result)

    def _print_system(self, system):
        return '{}'


class JSONPrinter(SerializedDataPrinter):
    def __init__(self,
                 query=QueryType.NONE,
                 verbosity=0,
                 palette=DefaultPalette(),
                 indentation=4):
        super().__init__(
            load_function=self._from_json,
            dump_function=self._to_json,
            query=query,
            verbosity=verbosity,
            palette=palette
        )

        self._indentation = indentation

    def _from_json(self, obj):
        return json.loads(obj)

    def _to_json(self, obj):
        return json.dumps(obj, indent=self._indentation)
