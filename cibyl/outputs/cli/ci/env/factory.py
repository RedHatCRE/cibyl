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
from cibyl.outputs.cli.ci.env.impl.colored import CIColoredPrinter
from cibyl.outputs.cli.ci.env.impl.serialized import JSONPrinter
from cibyl.utils.colors import ClearText


class CIPrinterFactory:
    """Factory for all types of :class:`CIPrinter`.
    """

    @staticmethod
    def from_style(style, query, verbosity, complete):
        """Builds the appropriate printer for the desired output style.

        :param style: The desired output style.
        :type style: :class:`OutputStyle`
        :param query: How far the hierarchy the printer shall go.
        :type query: :class:`cibyl.models.cli.QueryType`
        :param verbosity: Verbosity level.
        :type verbosity: int
        :param complete: Output mode. If enabled, prints extra information
        :type complete: bool
        :return: The printer.
        :rtype: :class:`cibyl.models.ci.printers.CIPrinter`
        :raise NotImplementedError: If there is no printer for the
            desired style.
        """
        if style == OutputStyle.TEXT:
            return CIColoredPrinter(
                query=query,
                verbosity=verbosity,
                palette=ClearText(),
                complete=complete
            )

        if style == OutputStyle.COLORIZED:
            return CIColoredPrinter(
                query=query,
                verbosity=verbosity,
                complete=complete
            )

        if style == OutputStyle.JSON:
            return JSONPrinter(
                query=query,
                verbosity=verbosity
            )

        raise NotImplementedError(f'Unknown output style: {style}')
