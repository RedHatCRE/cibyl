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
from cibyl.models.ci.printers import CIPrinter
from cibyl.models.ci.system import JobsSystem
from cibyl.publisher import PrintMode
from cibyl.utils.colors import DefaultPalette
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes

LOG = logging.getLogger(__name__)


class ColoredPrinter(CIPrinter):
    def __init__(self,
                 mode=PrintMode.COMPLETE, verbosity=0,
                 palette=DefaultPalette()):
        super().__init__(mode, verbosity)

        self._palette = palette

    @property
    def palette(self):
        return self._palette

    def print_environment(self, env):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Environment: '), 0)
        printer[0].append(env.name.value)

        for system in env.systems:
            if isinstance(system, JobsSystem):
                printer.add(self.print_jobs_system(system), 1)
            else:
                LOG.warning('Ignoring unknown system type: %s', type(system))
                continue

        return printer.build()

    def print_jobs_system(self, system):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), 0)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        if self.mode == PrintMode.COMPLETE:
            for job in system.jobs.values():
                printer.add(self.print_job(job), 1)

            printer.add(self._palette.blue('Total jobs found in query: '), 1)
            printer[-1].append(len(system.jobs))

        return printer.build()

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
                printer.add(value, 1)

        return printer.build()

    def print_build(self, build):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Build: '), 0)
        printer[0].append(build.build_id.value)

        if build.status.value:
            status_x_color_map = {
                'SUCCESS': lambda: self._palette.green(build.status.value),
                'FAILURE': lambda: self._palette.red(build.status.value),
                'UNSTABLE': lambda: self._palette.yellow(build.status.value)
            }

            status = status_x_color_map.get(
                build.status.value,
                lambda: self._palette.underline(build.status.value)
            )

            printer.add(self._palette.blue('Status: '), 1)
            printer[-1].append(status)

        if self.verbosity > 0:
            if build.duration.value:
                duration = as_minutes(build.duration.value)

                printer.add(self._palette.blue('Duration: '), 1)
                printer[-1].append(f'{duration:.2f}m')

        if build.tests.value:
            for test in build.test.values():
                printer.add(self.print_test(test), 1)

        return printer.build()

    def print_test(self, test):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Test: '), 0)
        printer[-1].append(test.name.value)

        if test.result.value:
            printer.add(self._palette.blue('Result: '), 1)

            if test.result.value in ['SUCCESS', 'PASSED']:
                printer[-1].append(self._palette.green(test.result.value))
            elif test.result.value in ['FAILURE', 'FAILED']:
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
