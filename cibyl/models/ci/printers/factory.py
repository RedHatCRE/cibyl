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
from cibyl.cli.output import OutputStyle
from cibyl.models.ci.printers.colored import CIColoredPrinter
from cibyl.models.ci.printers.raw import CIRawPrinter


class CIPrinterFactory:
    """Factory for :class:`CIPrinter`.
    """

    @staticmethod
    def from_style(style, mode, verbosity):
        """Builds the appropriate printer for the desired output style.

        :param style: The desired output style.
        :type style: :class:`OutputStyle`
        :param mode: Amount of desired information.
        :type mode: :class:`PrintMode`
        :param verbosity: Verbosity level.
        :type verbosity: int
        :return: The printer.
        :rtype: :class:`CIPrinter`
        :raise NotImplementedError: If there is not printer for the desired
            style.
        """
        if style == OutputStyle.TEXT:
            return CIRawPrinter(mode, verbosity)
        elif style == OutputStyle.COLORIZED:
            return CIColoredPrinter(mode, verbosity)
        else:
            raise NotImplementedError(f'Unknown output style: {style}')
