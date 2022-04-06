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

from cibyl.cli.output import OutputStyle
from cibyl.models.ci.printers.colored import ColoredPrinter
from cibyl.models.ci.printers.raw import RawPrinter

LOG = logging.getLogger(__name__)


class PrinterFactory:
    @staticmethod
    def from_style(style, verbosity):
        """

        :param style:
        :type style: :class:`OutputStyle`
        :param verbosity:
        :type verbosity: int
        :return:
        :rtype: :class:`cibyl.models.ci.printers.Printer`
        :raise NotImplementedError: If there is not printer for the desired
            style.
        """
        if style == OutputStyle.RAW:
            return RawPrinter(verbosity)
        elif style == OutputStyle.COLORED:
            return ColoredPrinter(verbosity)
        else:
            raise NotImplementedError(f'Unknown output style: {style}')


class Publisher:
    """Represents a publisher which is responsible for publishing the data
    collected by the application in the chosen format and to the chosen
    location
    """

    @staticmethod
    def publish(environments, output_style, dest="terminal", verbosity=0):
        """Publishes the data of the given environments to the
        chosen destination.
        """
        if dest == "terminal":
            for env in environments:
                printer = PrinterFactory.from_style(output_style, verbosity)

                print(printer.print_environment(env))
