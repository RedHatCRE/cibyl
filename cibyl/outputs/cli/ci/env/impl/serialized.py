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
import logging
from abc import ABC, abstractmethod

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.models.ci.base.system import JobsSystem
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    JSONBaseSystemPrinter
from cibyl.outputs.cli.ci.system.impls.jobs.serialized import \
    JSONJobsSystemPrinter

LOG = logging.getLogger(__name__)


class SerializedDataPrinter(CIPrinter, ABC):
    """Base class for printers that print a CI hierarchy in a format
    readable for machines, like JSON or YAML.
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
    def print_environment(self, env):
        def get_systems():
            systems = {}

            for system in env.systems:
                key = system.name.value
                systems[key] = self._load(self.print_system(system))

            return systems

        result = {
            'name': env.name.value,
            'systems': get_systems()
        }

        return self._dump(result)

    @abstractmethod
    def print_system(self, system):
        """
        :param system: The system.
        :type system: :class:`cibyl.models.ci.base.system.System`
        :return: Textual representation of the system.
        :rtype: str
        """
        raise NotImplementedError


class JSONPrinter(SerializedDataPrinter):
    """Serializer that prints a CI hierarchy in JSON format.
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

    @overrides
    def print_system(self, system):
        def get_printer():
            # Check specialized printers
            if isinstance(system, JobsSystem):
                return JSONJobsSystemPrinter(
                    self.query, self.verbosity, self.indentation
                )

            LOG.warning(
                'Custom printer not found for system of type: %s. '
                'Continuing with default printer...',
                type(system)
            )

            return JSONBaseSystemPrinter(
                self.query, self.verbosity, self.indentation
            )

        return get_printer().print_system(system)

    def _from_json(self, obj):
        return json.loads(obj)

    def _to_json(self, obj):
        return json.dumps(obj, indent=self._indentation)
