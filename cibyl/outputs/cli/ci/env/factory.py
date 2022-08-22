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
from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.env.impl.colored import CIColoredPrinter
from cibyl.outputs.cli.ci.env.impl.serialized import CIJSONPrinter
from cibyl.outputs.cli.ci.env.printer import CIPrinter
from cibyl.utils.colors import ClearText


class CIPrinterFactory:
    """Factory for all types of :class:`CIPrinter`.
    """

    @staticmethod
    def from_style(style: OutputStyle, query: QueryType,
                   verbosity: int) -> CIPrinter:
        """Builds the appropriate printer for the desired output style.

        :param style: The desired output style.
        :param query: How far the hierarchy the printer shall go.
        :param verbosity: Verbosity level.
        :return: The printer.
        :raise NotImplementedError: If there is no printer for the
            desired style.
        """
        if style == OutputStyle.TEXT:
            return CIColoredPrinter(
                query=query,
                verbosity=verbosity,
                palette=ClearText()
            )

        if style == OutputStyle.COLORIZED:
            return CIColoredPrinter(
                query=query,
                verbosity=verbosity
            )

        if style == OutputStyle.JSON:
            return CIJSONPrinter(
                query=query,
                verbosity=verbosity
            )

        raise NotImplementedError(f'Unknown output style: {style}')
