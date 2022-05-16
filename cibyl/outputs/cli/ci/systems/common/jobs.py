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
    If it is not, most likely calling :func:`get_plugin_section` ends in an
    empty string.

    :param job: The job to check.
    :type job: :class:`cibyl.models.ci.base.job.Job`
    :return: True if you should get the plugins' section for this job,
        False if not.
    :rtype: bool
    """
    return job.plugin_attributes


def get_plugin_section(printer, job):
    """Gets the text describing the plugins that affect a job.

    :param printer: The printer the text will be based on. The output of
        this function will follow the styling of this.
    :type printer: :class:`cibyl.outputs.cli.printer.ColoredPrinter`
    :param job: The job get the description for.
    :type job: :class:`cibyl.models.ci.base.job.Job`
    :return: The description.
    :rtype: str
    """
    text = IndentedTextBuilder()

    for plugin in job.plugin_attributes:
        # Plugins are installed as part of the model
        attribute = getattr(job, plugin)

        # Check if the plugin is installed
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
