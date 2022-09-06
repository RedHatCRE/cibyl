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
from typing import Union

from cibyl.cli.output import OutputStyle
from cibyl.models.attribute import (AttributeDictValue, AttributeListValue,
                                    AttributeValue)
from cibyl.models.model import Model
from cibyl.outputs.cli.printer import JSON, ColoredPrinter, SerializedPrinter
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


def get_plugin_section(
    style: OutputStyle,
    model: Model,
    reference: Union[ColoredPrinter, SerializedPrinter[JSON]]
) -> str:
    """Gets the text describing the plugins that affect a model.

    ..  seealso::
        See :func:`has_plugin_section`.

    :param style: Desired format of output by the plugin.
    :param model: The model to get the description for.
    :param reference: The printer the text will be based on. The output of
        this function will follow the styling of this.
    :return: The description.
    :raises ValueError: If the model does not have enough data to build the
        section.
    """
    if not has_plugin_section(model):
        raise ValueError('Job is missing plugin attributes.')

    for plugin_attribute in model.plugin_attributes:
        # Plugins install some attributes as part of the model
        plugin = model.plugin_attributes[plugin_attribute]
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

        printer = plugin['printer']

        if style in (OutputStyle.TEXT, OutputStyle.COLORIZED):
            result = IndentedTextBuilder()

            for value in values:
                data = printer.as_text(
                    model=value,
                    config=reference.config
                )

                result.add(f"{data}", 0)

            return result.build()

        if style in (OutputStyle.JSON,):
            result = IndentedTextBuilder()
            result.add('{', 0)

            for value in values:
                data = printer.as_json(
                    model=value,
                    provider=reference.provider,
                    config=reference.config
                )

                result.add(f"\"{plugin['name']}\": {data}", 1)

            result.add('}', 0)
            return result.build()

        raise NotImplementedError(f"Unknown style: '{style}'.")
