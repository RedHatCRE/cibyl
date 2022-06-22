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

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.colors import DefaultPalette


class JSONPrinter(ColoredPrinter, CIPrinter):
    def __init__(self,
                 query=QueryType.NONE,
                 verbosity=0,
                 palette=DefaultPalette(),
                 indentation=2):
        super().__init__(query, verbosity, palette)

        self._indentation = indentation

    @overrides
    def print_environment(self, env):
        result = {
            'name': env.name.value
        }

        return self._to_json(result)

    def print_system(self, system):
        return ''

    def _to_json(self, obj):
        return json.dumps(obj, indent=self._indentation)
