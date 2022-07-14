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

from cibyl.models.attribute import (AttributeDictValue, AttributeListValue,
                                    AttributeValue)
from cibyl.models.model import Model
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.printers.colored import OSColoredPrinter
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


def has_plugin_section(model: Model) -> bool:
    """Checks whether a model is worth having a plugins' section for.

    :param model: The model to check.
    :return: True if the model has enough data to build
        a plugins' section with, False if not.
    """
    if not model.plugin_attributes:
        return False
    has_plugin_attribute = False
    for plugin_attribute in model.plugin_attributes:
        # Plugins install some attributes as part of the model
        attribute = getattr(model, plugin_attribute)

        # Check if the attribute is populated
        if not attribute.value:
            continue
        has_plugin_attribute = True
    return has_plugin_attribute


def get_plugin_section(printer: ColoredPrinter, model: Model) -> str:
    """Gets the text describing the plugins that affect a model.

    ..  seealso::
        See :func:`has_plugin_section`.

    :param printer: The printer the text will be based on. The output of
        this function will follow the styling of this.
    :param model: The model to get the description for.
    :return: The description.
    :raises ValueError: If the model does not have enough data to build the
        section.
    """
    if not has_plugin_section(model):
        raise ValueError('Job is missing plugin attributes.')

    text = IndentedTextBuilder()

    for plugin_attribute in model.plugin_attributes:
        # Plugins install some attributes as part of the model
        attribute = getattr(model, plugin_attribute)

        # Check if the attribute is populated
        if not attribute.value:
            continue

        if isinstance(attribute, AttributeValue):
            values = [attribute.value]
        elif isinstance(attribute, AttributeListValue):
            values = attribute.value
        elif isinstance(attribute, AttributeDictValue):
            values = attribute.value.values()
        else:
            LOG.warning(
                'Ignoring unknown attribute type: %s', type(attribute)
            )
            continue

        for value in values:
            if isinstance(value, Deployment):
                os_printer = OSColoredPrinter(
                    printer.query, printer.verbosity, printer.palette
                )

                text.add(os_printer.print_deployment(value), 0)
            else:
                LOG.warning(
                    'Ignoring unknown plugin type: %s', type(value)
                )
                continue

    return text.build()
