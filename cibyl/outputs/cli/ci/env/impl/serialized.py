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
from abc import ABC, abstractmethod

from overrides import overrides

from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    JSONBaseSystemPrinter
from cibyl.outputs.cli.ci.system.impls.jobs.serialized import \
    JSONJobsSystemPrinter
from cibyl.outputs.cli.printer import SerializedPrinter, JSONPrinter

LOG = logging.getLogger(__name__)


class CISerializedPrinter(CIPrinter, SerializedPrinter, ABC):
    """Base class for printers that print a CI hierarchy in a format
    readable for machines, like JSON or YAML.
    """

    @overrides
    def print_environment(self, env: Environment) -> str:
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
    def print_system(self, system: System) -> str:
        """
        :param system: The system.
        :return: Textual representation of the system.
        """
        raise NotImplementedError


class CIJSONPrinter(JSONPrinter, CISerializedPrinter):
    """Serializer that prints a CI hierarchy in JSON format.
    """

    @overrides
    def print_system(self, system: System) -> str:
        def get_printer():
            # Check specialized printers
            if isinstance(system, JobsSystem):
                return JSONJobsSystemPrinter(
                    query=self.query,
                    verbosity=self.verbosity,
                    indentation=self.indentation
                )

            LOG.warning(
                'Custom printer not found for system of type: %s. '
                'Continuing with default printer...',
                type(system)
            )

            return JSONBaseSystemPrinter(
                query=self.query,
                verbosity=self.verbosity,
                indentation=self.indentation
            )

        return get_printer().print_system(system)
