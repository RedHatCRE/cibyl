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
from overrides import overrides

from cibyl.models.model import Model
from cibyl.outputs.cli.printer import JSON, ColoredPrinter, SerializedPrinter
from cibyl.plugins import PluginPrinterTemplate
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.printers.colored import OSColoredPrinter
from cibyl.plugins.openstack.printers.serialized import OSJSONPrinter


class PrinterRouter(PluginPrinterTemplate):
    """Takes care of redirecting the printing petition to the appropriate
    printer on this plugin.
    """

    @overrides
    def as_text(
        self,
        model: Model,
        config: ColoredPrinter.Config
    ) -> str:
        if isinstance(model, Deployment):
            printer = OSColoredPrinter(
                query=config.query,
                verbosity=config.verbosity,
                palette=config.palette
            )

            return printer.print_deployment(model)

        raise NotImplementedError(f"Unknown model: '{type(model).__name__}'.")

    @overrides
    def as_json(
        self,
        model: Model,
        provider: JSON,
        config: SerializedPrinter.Config
    ) -> str:
        if isinstance(model, Deployment):
            printer = OSJSONPrinter(
                provider=provider,
                query=config.query,
                verbosity=config.verbosity
            )

            return printer.print_deployment(model)

        raise NotImplementedError(f"Unknown model: '{type(model).__name__}'.")
