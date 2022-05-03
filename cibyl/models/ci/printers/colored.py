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

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.models.attribute import (AttributeDictValue, AttributeListValue,
                                    AttributeValue)
from cibyl.models.ci.printers import CIPrinter
from cibyl.models.ci.system import JobsSystem, ZuulSystem
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.printers.colored import OSColoredPrinter
from cibyl.utils.colors import DefaultPalette
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes

LOG = logging.getLogger(__name__)


class CIColoredPrinter(CIPrinter):
    """Provides a human-readable representation of CI models decorated with
    coloring for easier readability.
    """

    def __init__(self,
                 query=QueryType.NONE, verbosity=0,
                 palette=DefaultPalette()):
        """Constructor.

        See parents for more information.

        :param palette: Palette of colors to be used.
        :type palette: :class:`cibyl.utils.colors.ColorPalette`
        """
        super().__init__(query, verbosity)

        self._palette = palette

    @property
    def palette(self):
        """
        :return: The palette currently in use.
        :rtype: :class:`cibyl.utils.colors.ColorPalette`
        """
        return self._palette

    @overrides
    def print_environment(self, env):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Environment: '), 0)
        printer[0].append(env.name.value)

        for system in env.systems:
            printer.add(self.print_system(system), 1)

        return printer.build()

    @overrides
    def print_system(self, system):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), 0)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        # Print type specific contents
        if isinstance(system, JobsSystem):
            printer.add(self._print_jobs_system(system), 1)
        elif isinstance(system, ZuulSystem):
            printer.add(self._print_zuul_system(system), 1)
        else:
            LOG.warning('Ignoring unknown system: %s', type(system).__name__)

        return printer.build()

    def _print_jobs_system(self, system):
        printer = IndentedTextBuilder()

        if self.query != QueryType.NONE:
            for job in system.jobs.values():
                printer.add(self.print_job(job), 1)

            if system.is_queried():
                header = 'Total jobs found in query: '

                printer.add(self._palette.blue(header), 1)
                printer[-1].append(len(system.jobs))
            else:
                printer.add(self._palette.blue('No query performed'), 1)

        return printer.build()

    def _print_zuul_system(self, system):
        printer = IndentedTextBuilder()

        if self.query != QueryType.NONE:
            for tenant in system.tenants.values():
                printer.add(self.print_tenant(tenant), 1)

            if system.is_queried():
                header = 'Total tenants found in query: '

                printer.add(self._palette.blue(header), 1)
                printer[-1].append(len(system.tenants))
            else:
                printer.add(self._palette.blue('No query performed'), 1)

        return printer.build()

    @overrides
    def print_tenant(self, tenant):
        result = IndentedTextBuilder()

        result.add(self._palette.blue('Tenant: '), 0)
        result[-1].append(tenant.name.value)

        if self.query > QueryType.TENANTS:
            for job in tenant.jobs.values():
                result.add(self.print_job(job), 1)

            result.add(
                self._palette.blue("Total jobs found in tenant '"), 1
            )

            result[-1].append(self._palette.underline(tenant.name.value))
            result[-1].append(self._palette.blue("': "))
            result[-1].append(len(tenant.jobs))

        return result.build()

    def print_project(self, project):
        result = IndentedTextBuilder()

        result.add(self._palette.blue('Project: '), 0)
        result[-1].append(project.name.value)

        if self.query > QueryType.PROJECTS:
            for pipeline in project.pipelines.values():
                result.add(self.print_pipeline(pipeline), 1)

            result.add(
                self._palette.blue("Total pipelines found in project '"), 1
            )

            result[-1].append(self._palette.underline(project.name.value))
            result[-1].append(self._palette.blue("': "))
            result[-1].append(len(project.pipelines))

    @overrides
    def print_pipeline(self, pipeline):
        result = IndentedTextBuilder()

        result.add(self._palette.blue('Pipeline: '), 0)
        result[-1].append(pipeline.name.value)

        if self.query > QueryType.PIPELINES:
            for job in pipeline.jobs.values():
                result.add(self.print_job(job), 1)

            result.add(
                self._palette.blue('Total jobs found in pipeline '), 1
            )

            result[-1].append(self._palette.underline(pipeline.name.value))
            result[-1].append(self._palette.blue(': '))
            result[-1].append(len(pipeline.jobs))

        return result.build()

    @overrides
    def print_job(self, job):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Job: '), 0)
        printer[-1].append(job.name.value)

        if self.verbosity > 0:
            if job.url.value:
                printer.add(self._palette.blue('URL: '), 1)
                printer[-1].append(job.url.value)

        if job.builds.value:
            for build in job.builds.values():
                printer.add(self.print_build(build), 1)

        for plugin in job.plugin_attributes:
            # Plugins are installed as part of the model
            attribute = getattr(job, plugin)

            # Check if the plugin is installed
            if not attribute.value:
                LOG.debug(
                    'Could not retrieve value for %s on %s.',
                    plugin, job.name.value
                )
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
                        self.query, self.verbosity, self.palette
                    )

                    printer.add(os_printer.print_deployment(value), 1)
                else:
                    LOG.warning(
                        'Ignoring unknown plugin type: %s', type(value)
                    )
                    continue

        return printer.build()

    @overrides
    def print_build(self, build):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Build: '), 0)
        printer[0].append(build.build_id.value)

        if build.status.value:
            status_x_color_map = {
                'SUCCESS': lambda: self._palette.green(build.status.value),
                'FAILURE': lambda: self._palette.red(build.status.value),
                'UNSTABLE': lambda: self._palette.yellow(
                    build.status.value)
            }

            status = status_x_color_map.get(
                build.status.value,
                lambda: self._palette.underline(build.status.value)
            )()

            printer.add(self._palette.blue('Status: '), 1)
            printer[-1].append(status)

        if self.verbosity > 0:
            if build.duration.value:
                duration = as_minutes(build.duration.value)

                printer.add(self._palette.blue('Duration: '), 1)
                printer[-1].append(f'{duration:.2f}m')

        if build.tests.value:
            for test in build.tests.values():
                printer.add(self.print_test(test), 1)

        return printer.build()

    @overrides
    def print_test(self, test):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Test: '), 0)
        printer[-1].append(test.name.value)

        if test.result.value:
            printer.add(self._palette.blue('Result: '), 1)

            if test.result.value in ['SUCCESS', 'PASSED']:
                printer[-1].append(self._palette.green(test.result.value))
            elif test.result.value in ['FAILURE', 'FAILED', 'REGRESSION']:
                printer[-1].append(self._palette.red(test.result.value))
            elif test.result.value == "UNSTABLE":
                printer[-1].append(self._palette.yellow(test.result.value))
            elif test.result.value == "SKIPPED":
                printer[-1].append(self._palette.blue(test.result.value))

        if test.class_name.value:
            printer.add(self._palette.blue('Class name: '), 1)
            printer[-1].append(test.class_name.value)

        if self.verbosity > 0:
            if test.duration.value:
                duration = as_minutes(test.duration.value)

                printer.add(self._palette.blue('Duration: '), 1)
                printer[-1].append(f'{duration:.2f}m')

        return printer.build()
