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
from typing import Optional

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    JSONBaseSystemPrinter
from cibyl.outputs.cli.ci.system.impls.jobs.serialized import \
    JSONJobsSystemPrinter
from cibyl.outputs.cli.ci.system.impls.zuul.serialized import \
    JSONZuulSystemPrinter
from cibyl.outputs.cli.printer import JSON, PROV, STDJSON, SerializedPrinter

LOG = logging.getLogger(__name__)


class CISerializedPrinter(
    SerializedPrinter[PROV],
    CIPrinter,
    ABC
):
    """Base class for printers that print a CI hierarchy in a format
    readable for machines, like JSON or YAML.
    """

    @overrides
    def print_environment(self, env: Environment) -> str:
        def get_systems():
            systems = {}

            for system in env.systems:
                key = system.name.value
                systems[key] = self.provider.load(self.print_system(system))

            return systems

        result = {
            'name': env.name.value,
            'systems': get_systems()
        }

        return self.provider.dump(result)

    @abstractmethod
    def print_system(self, system: System) -> str:
        """
        :param system: The system.
        :return: Textual representation of the system.
        """
        raise NotImplementedError


class CIJSONPrinter(CISerializedPrinter[JSON]):
    """Serializer that prints a CI hierarchy in JSON format.
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

    @overrides
    def print_system(self, system: System) -> str:
        def get_printer():
            # Check specialized printers
            if isinstance(system, JobsSystem):
                return JSONJobsSystemPrinter(
                    provider=self.provider,
                    query=self.query,
                    verbosity=self.verbosity
                )

            if isinstance(system, ZuulSystem):
                return JSONZuulSystemPrinter(
                    provider=self.provider,
                    query=self.query,
                    verbosity=self.verbosity
                )

            LOG.warning(
                'Custom printer not found for system of type: %s. '
                'Continuing with default printer...',
                type(system)
            )

            return JSONBaseSystemPrinter(
                provider=self.provider,
                query=self.query,
                verbosity=self.verbosity
            )

        return get_printer().print_system(system)
