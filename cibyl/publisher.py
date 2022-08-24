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
from enum import Enum

from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.environment import Environment
from cibyl.outputs.cli.ci.env.factory import CIPrinterFactory

LOG = logging.getLogger(__name__)


class PublisherTarget(Enum):
    TERMINAL = 0
    FILE = 1


class Publisher:
    """Represents a publisher which is responsible for publishing the data
    collected by the application in the chosen format and to the chosen
    location
    """

    def publish(self,
                environment: Environment,
                target: PublisherTarget = PublisherTarget.TERMINAL,
                style: OutputStyle = OutputStyle.TEXT,
                query: QueryType = QueryType.NONE,
                verbosity: int = 0, **kwargs) -> None:
        """Publishes the data of the given environments to the
        chosen destination.
        """
        printer = CIPrinterFactory.from_style(style, query, verbosity)
        output = printer.print_environment(environment)

        if target == PublisherTarget.TERMINAL:
            LOG.info("Writing output into console...")
            print(output)
            return

        if target == PublisherTarget.FILE:
            file = kwargs['output_path']
            LOG.info("Writing output to: '%s'...", file)
            # add newline to the end out the output that is not added by the
            # printers
            file.append(output+'\n')
            return

        raise NotImplementedError(f"Unhandled target: '{target}'.")
