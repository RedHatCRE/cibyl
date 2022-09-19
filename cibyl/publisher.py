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
from enum import Enum
from typing import Optional, Union

from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.environment import Environment
from cibyl.outputs.cli.ci.env.factory import CIPrinterFactory
from cibyl.utils.fs import File

LOG = logging.getLogger(__name__)


class PublisherTarget(Enum):
    TERMINAL = 0
    FILE = 1


class Publisher(ABC):
    """Represents a publisher which is responsible for publishing the data
    collected by the application in the chosen format and to the chosen
    location.
    """

    def __init__(self, target: PublisherTarget = PublisherTarget.TERMINAL,
                 style: OutputStyle = OutputStyle.TEXT,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0, output_file: Optional[File] = None):
        self.target = target
        self.style = style
        self.query = query
        self.verbosity = verbosity
        self.output_file = output_file
        self.printer = CIPrinterFactory.from_style(self.style, self.query,
                                                   self.verbosity)

    @abstractmethod
    def publish(self, environment: Environment) -> None:
        """Publishes the data of the given environments to the
        chosen destination.
        """
        raise NotImplementedError

    def finish_publishing(self):
        """Method to print all the output for output styles that must collect
        the output for all environments, like the json one. It will do nothing
        for the other styles, like text or colored."""
        pass

    def _generate_environment_output(self, environment: Environment) -> str:
        """Generate a string representation of the environment in the desired
        style (text, colored, json...)

        :returns: The string representation of the environment
        """
        return self.printer.print_environment(environment)

    def _print_output(self, output: str) -> None:
        """Print the contents of the output string to the desired
        destination."""
        if self.target == PublisherTarget.TERMINAL:
            LOG.info("Writing output into console...")
            print(output)
            return

        if self.target == PublisherTarget.FILE:
            LOG.info("Writing output to: '%s'...", self.output_file)
            # add newline to the end out the output that is not added by the
            # printers
            self.output_file.append(output+'\n')
            return

        raise NotImplementedError(f"Unhandled target: '{self.target}'.")


class PrintPublisher(Publisher):
    """Publisher for text output, it supports both colored and raw text. It
    prints the output after each query finishes, either to
    file or to stdout."""

    def publish(self, environment: Environment) -> None:
        """Publishes the data of the given environments to the
        chosen destination.
        """
        output = self._generate_environment_output(environment)
        self._print_output(output)


class JSONPublisher(Publisher):
    """Publisher for JSON output. It prints all the output after all queries
    have finished in a single json object."""

    def __init__(self, target: PublisherTarget = PublisherTarget.TERMINAL,
                 style: OutputStyle = OutputStyle.JSON,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0, output_file: Optional[File] = None):
        super().__init__(target=target, style=style, query=query,
                         verbosity=verbosity, output_file=output_file)
        self.output = []

    def publish(self, environment: Environment) -> None:
        """Store the JSON representation of the environment for later printing.
        """
        self.output.append(self._generate_environment_output(environment))

    def finish_publishing(self) -> None:
        """Method to print all the output for output styles that must collect
        the output for all environments, like the json one."""
        envs = [json.loads(env) for env in self.output]
        final_output = {'environments': envs}
        self._print_output(
            json.dumps(
                final_output,
                indent=self.printer.provider.indentation
            )
        )


PUBLISHER_TYPE = Union[PrintPublisher, JSONPublisher]


class PublisherFactory:
    """Create the apropiate publisher according to user input."""
    @staticmethod
    def create_publisher(target: PublisherTarget = PublisherTarget.TERMINAL,
                         style: OutputStyle = OutputStyle.TEXT,
                         query: QueryType = QueryType.NONE,
                         verbosity: int = 0,
                         output_file: Optional[File] = None) -> PUBLISHER_TYPE:
        if style in (OutputStyle.JSON,):
            return JSONPublisher(target=target, style=style, query=query,
                                 verbosity=verbosity, output_file=output_file)
        else:
            return PrintPublisher(target=target, style=style, query=query,
                                  verbosity=verbosity, output_file=output_file)
