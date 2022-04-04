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
from abc import ABC, abstractmethod

from cibyl.models.attribute import AttributeValue, AttributeListValue, \
    AttributeDictValue
from cibyl.models.ci.printers import Printer
from cibyl.models.ci.system import JobsSystem
from cibyl.utils.colors import Colors
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColorProvider(ABC):
    @abstractmethod
    def red(self, text):
        raise NotImplementedError

    @abstractmethod
    def green(self, text):
        raise NotImplementedError

    @abstractmethod
    def blue(self, text):
        raise NotImplementedError

    @abstractmethod
    def yellow(self, text):
        raise NotImplementedError

    @abstractmethod
    def underline(self, text):
        raise NotImplementedError


class ColoredText(ColorProvider):
    def red(self, text):
        return Colors.red(text)

    def green(self, text):
        return Colors.green(text)

    def blue(self, text):
        return Colors.blue(text)

    def yellow(self, text):
        return Colors.yellow(text)

    def underline(self, text):
        return Colors.underline(text)


class ColoredPrinter(Printer):
    def __init__(self, verbosity=0, color=ColoredText()):
        super().__init__(verbosity)

        self._color = color

    def print_environment(self, env):
        printer = IndentedTextBuilder()

        printer.add(f'{self._color.blue("Environment: ")}{env.name.value}', 0)

        for system in env.systems:
            if isinstance(system, JobsSystem):
                printer.add(self.print_jobs_system(system), 1)
            else:
                LOG.warning('Ignoring unknown system type: %s', type(system))
                continue

        return printer.build()

    def print_jobs_system(self, system):
        printer = IndentedTextBuilder()

        printer.add(f'{self._color.blue("System: ")}{system.name.value}', 0)

        if self.verbosity > 0:
            printer[0].append(f' (type: {system.system_type.value})')

        for job in system.jobs.values():
            printer.add(self.print_job(job), 1)

        if self.verbosity > 1:
            printer.add(f'Total jobs: {len(system.jobs)}', 0)

        return printer.build()

    def print_job(self, job):
        printer = IndentedTextBuilder()

        printer.add(f'{self._color.blue("Job: ")}{job.name.value}', 0)

        if self.verbosity > 0:
            if job.url.value:
                printer.add(f'URL: {job.url.value}', 1)

        if job.builds.value:
            for build in job.builds.values():
                printer.add(self.print_build(build), 1)

        for plugin in job.plugin_attributes:
            # Plugins are installed as part of the model
            attribute = getattr(job, plugin)

            # Check if the plugin is installed
            if not attribute.value:
                LOG.debug(
                    f'Could not retrieve value for %s on %s.',
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

        return printer

    def print_build(self, build):
        printer = IndentedTextBuilder()

        printer.add(f'{self._color.blue("Build: ")}{build.build_id.value}', 0)

        if build.status.value:
            status_x_color_map = {
                'SUCCESS': lambda: self._color.green(build.status.value),
                'FAILURE': lambda: self._color.red(build.status.value),
                'UNSTABLE': lambda: self._color.yellow(build.status.value)
            }

            status = status_x_color_map.get(
                build.status.value,
                lambda: self._color.underline(build.status.value)
            )

            printer.add(f'{self._color.blue("Status: ")}{status}', 1)

        if self.verbosity > 0:
            if build.duration.value:
                def as_minutes(ms):
                    return ms / 60000

                duration = as_minutes(build.duration.value)

                printer.add(
                    f'{self._color.blue("Duration: ")}{duration:.2f}', 1
                )

        return printer.build()
