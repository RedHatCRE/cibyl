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

import cibyl.outputs.cli.ci.system.common.features as features_queries
from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.system import System
from cibyl.models.ci.base.test import Test
from cibyl.outputs.cli.ci.system.common.builds import (get_duration_section,
                                                       get_status_section)
from cibyl.outputs.cli.ci.system.common.models import (get_plugin_section,
                                                       has_plugin_section)
from cibyl.outputs.cli.ci.system.common.stages import print_stage
from cibyl.outputs.cli.ci.system.impls.base.colored import \
    ColoredBaseSystemPrinter
from cibyl.utils.sorting import nsort, sort
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes


class ColoredJobsSystemPrinter(ColoredBaseSystemPrinter):
    """Printer meant for :class:`JobsSystem`, decorated with colors for
    easier read.
    """

    @overrides
    def print_system(self, system: System) -> str:
        printer = IndentedTextBuilder()

        # Begin with the text common to all systems
        printer.add(super().print_system(system), 0)

        if self.query != QueryType.NONE:
            for job in sort(system.jobs.values(), self._job_sorter):
                printer.add(self.print_job(job), 1)

            if not system.is_queried():
                printer.add(self.palette.blue('No query performed'), 1)
            elif not features_queries.is_pure_features_query(self.query):
                # avoid printing the number of jobs in case of having requested
                # only features without jobs flag
                header = 'Total jobs found in query: '

                printer.add(self.palette.blue(header), 1)
                printer[-1].append(len(system.jobs))

        return printer.build()

    def print_job(self, job: Job) -> str:
        """
        :param job: The job.
        :return: Textual representation of the provided model.
        """
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Job: '), 0)
        printer[-1].append(job.name.value)

        if self.verbosity > 0:
            if job.url.value:
                printer.add(self.palette.blue('URL: '), 1)
                printer[-1].append(job.url.value)

        if features_queries.is_features_query(self.query):
            # if features are used, do not print further below
            return printer.build()

        if self.query >= QueryType.BUILDS:
            if job.builds.value:
                for build in nsort(job.builds.values(), self._build_sorter):
                    printer.add(self.print_build(build), 1)
            else:
                msg = 'No builds in query.'
                printer.add(self.palette.red(msg), 1)

        if has_plugin_section(job):
            printer.add(get_plugin_section(OutputStyle.TEXT, job, self), 1)

        return printer.build()

    def print_build(self, build: Build) -> str:
        """
        :param build: The build.
        :return: Textual representation of the provided model.
        """
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Build: '), 0)
        printer[0].append(build.build_id.value)

        if build.status.value:
            printer.add(get_status_section(self.palette, build), 1)

        if self.verbosity > 0:
            if build.duration.value:
                printer.add(get_duration_section(self.palette, build), 1)

        if self.query >= QueryType.TESTS:
            if build.tests.value:
                for test in build.tests.values():
                    printer.add(self.print_test(test), 1)
            else:
                msg = 'No tests in query.'
                printer.add(self.palette.red(msg), 1)

        if build.stages.value:
            printer.add(self.palette.blue('Stages: '), 1)
            for stage in build.stages:
                printer.add(print_stage(stage, self.palette,
                                        self.verbosity), 2)

        return printer.build()

    def print_test(self, test: Test) -> str:
        """
        :param test: The test.
        :return: Textual representation of the provided model.
        """
        printer = IndentedTextBuilder()

        printer.add(self.palette.blue('Test: '), 0)
        printer[-1].append(test.name.value)

        if test.result.value:
            printer.add(self.palette.blue('Result: '), 1)

            if test.result.value in ['SUCCESS', 'PASSED']:
                printer[-1].append(self.palette.green(test.result.value))
            elif test.result.value in ['FAILURE', 'FAILED', 'REGRESSION']:
                printer[-1].append(self.palette.red(test.result.value))
            elif test.result.value == "UNSTABLE":
                printer[-1].append(self.palette.yellow(test.result.value))
            elif test.result.value == "SKIPPED":
                printer[-1].append(self.palette.blue(test.result.value))

        if test.class_name.value:
            printer.add(self.palette.blue('Class name: '), 1)
            printer[-1].append(test.class_name.value)

        if self.verbosity > 0:
            if test.duration.value:
                duration = as_minutes(test.duration.value)

                printer.add(self.palette.blue('Duration: '), 1)
                printer[-1].append(f'{duration:.2f}min')

        return printer.build()
