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
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.outputs.cli.ci.systems.base.colored import ColoredBaseSystemPrinter
from cibyl.outputs.cli.ci.systems.zuul.colored import ColoredZuulSystemPrinter


class ColoredSystemPrinterFactory:
    def __init__(self, parent):
        """

        :param parent:
        :type parent: :class:`cibyl.outputs.cli.ci.colored.CIColoredPrinter`
        """
        self._parent = parent

    def from_system(self, system):
        if isinstance(system, ZuulSystem):
            return ColoredZuulSystemPrinter(
                query=self._parent.query,
                verbosity=self._parent.verbosity,
                palette=self._parent.palette
            )

        return ColoredBaseSystemPrinter(
            query=self._parent.query,
            verbosity=self._parent.verbosity,
            palette=self._parent.palette
        )
