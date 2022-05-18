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
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.printers.colored import OSColoredPrinter
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


def has_plugin_section(job):
    """Checks whether a job is worth having a plugins' section for.

    :param job: The job to check.
    :type job: :class:`cibyl.models.ci.base.job.Job`
    :return: True if the job has enough data to build a plugins' section with,
        False if not.
    :rtype: bool
    """
    if not job.plugin_attributes:
        return False
    has_plugin_attribute = False
    for plugin_attribute in job.plugin_attributes:
        # Plugins install some attributes as part of the model
        attribute = getattr(job, plugin_attribute)

        # Check if the attribute is populated
        if not attribute.value:
            continue
        has_plugin_attribute = True
    return has_plugin_attribute


def get_plugin_section(printer, job):
    """Gets the text describing the plugins that affect a job.

    ..  seealso::
        See :func:`has_plugin_section`.

    :param printer: The printer the text will be based on. The output of
        this function will follow the styling of this.
    :type printer: :class:`cibyl.outputs.cli.printer.ColoredPrinter`
    :param job: The job get the description for.
    :type job: :class:`cibyl.models.ci.base.job.Job`
    :return: The description.
    :rtype: str
    :raises ValueError: If the job does not have enough data to build the
        section.
    """
    if not has_plugin_section(job):
        raise ValueError('Job is missing plugin attributes.')

    text = IndentedTextBuilder()

    for plugin_attribute in job.plugin_attributes:
        # Plugins install some attributes as part of the model
        attribute = getattr(job, plugin_attribute)

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

                text.add(os_printer.print_deployment(value), 1)
            else:
                LOG.warning(
                    'Ignoring unknown plugin type: %s', type(value)
                )
                continue

    return text.build()
