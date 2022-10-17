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
import cibyl.outputs.cli.ci.system.common.features as features_query
from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.test import Test, TestKind, TestStatus
from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.outputs.cli.ci.system.common.builds import (get_duration_section,
                                                       get_status_section)
from cibyl.outputs.cli.ci.system.common.models import (get_plugin_section,
                                                       has_plugin_section)
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes


class JobCascade(ColoredPrinter):
    """Printer meant for :class:`Job` and all of its children. This
    printer focused on giving as much information as possible on each
    element.
    """

    def print_job(self, job: Job) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Job: '), 0)
        result[-1].append(job.name.value)

        if features_query.is_features_query(self.query):
            # if features are used, do not print further below
            return result.build()

        if self.verbosity > 0:
            if job.url.value:
                result.add(self.palette.blue('URL: '), 1)
                result[-1].append(job.url.value)

        if job.variants.value:
            result.add(self.palette.blue('Variants: '), 1)

            for variant in job.variants:
                result.add(self.print_variant(variant), 2)

        if self.query >= QueryType.BUILDS:
            if job.builds.value:
                result.add(self.palette.blue('Builds: '), 1)

                for build in job.builds.values():
                    result.add(self.print_build(build), 2)
            else:
                msg = 'No builds in query.'
                result.add(self.palette.red(msg), 1)

        return result.build()

    def print_variant(self, variant: Job.Variant) -> str:
        result = IndentedTextBuilder()
        result.add(self.palette.blue('Variant: '), 0)

        result.add(self.palette.blue('Description: '), 1)
        result[-1].append(variant.description)

        result.add(self.palette.blue('Parent: '), 1)
        result[-1].append(variant.parent)

        result.add(self.palette.blue('Branches: '), 1)
        for branch in variant.branches:
            result.add('- ', 2)
            result[-1].append(branch)

        result.add(self.palette.blue('Variables: '), 1)
        for key, value in variant.variables.items():
            result.add(self.palette.blue(f'{key}: '), 2)
            result[-1].append(value)

        if has_plugin_section(variant):
            result.add(
                text=get_plugin_section(OutputStyle.TEXT, variant, self),
                level=1
            )

        return result.build()

    def print_build(self, build: Build) -> str:
        result = IndentedTextBuilder()
        result.add(self.palette.blue('Build: '), 0)
        result[0].append(build.build_id.value)

        if build.project.value:
            result.add(self.palette.blue('Project: '), 1)
            result[-1].append(build.project.value)

        if build.pipeline.value:
            result.add(self.palette.blue('Pipeline: '), 1)
            result[-1].append(build.pipeline.value)

        if build.status.value:
            result.add(get_status_section(self.palette, build), 1)

        if self.verbosity > 0:
            if build.duration.value:
                result.add(get_duration_section(self.palette, build), 1)

        if self.query >= QueryType.TESTS:
            result.add(self.palette.blue('Test Suites: '), 1)

            if build.suites:
                for suite in build.suites:
                    result.add(self.print_suite(suite), 2)
            else:
                msg = 'No tests in query.'
                result.add(self.palette.red(msg), 2)

        return result.build()

    def print_suite(self, suite: TestSuite) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Test Suite: '), 0)

        if suite.name.value:
            result.add(self.palette.blue('Name: '), 1)
            result[-1].append(suite.name.value)

        result.add(self.palette.blue('Tests: '), 1)
        result[-1].append(suite.test_count)

        result.add(self.palette.blue('Succeeded: '), 1)
        result[-1].append(suite.success_count)

        result.add(self.palette.blue('Failed: '), 1)
        result[-1].append(suite.failed_count)

        result.add(self.palette.blue('Skipped: '), 1)
        result[-1].append(suite.skipped_count)

        if self.verbosity > 0:
            if suite.url.value:
                result.add(self.palette.blue('URL: '), 1)
                result[-1].append(suite.url.value)

        if suite.tests:
            result.add(self.palette.blue('Tests: '), 1)

            for test in suite.tests:
                result.add(self.print_test(test), 2)

        return result.build()

    def print_test(self, test: Test) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Test: '), 0)

        if self.verbosity > 0:
            result.add(self.palette.blue('Type: '), 1)
            result[-1].append(self._get_colored_test_kind(test.kind.value))

        result.add(self.palette.blue('Name: '), 1)
        result[-1].append(test.name.value)

        if self.verbosity > 0:
            result.add(self.palette.blue('Duration: '), 1)
            duration = as_minutes(test.duration.value, unit="s")
            result[-1].append(f'{duration:.2f}min')

        result.add(self.palette.blue('Result: '), 1)
        result[-1].append(self._get_colored_test_result(test.result.value))

        if test.class_name.value:
            result.add(self.palette.blue('Class name: '), 1)
            result[-1].append(test.class_name.value)
        if self.verbosity > 1:
            result.add(self.palette.blue('URL: '), 1)
            result[-1].append(test.url.value)

        return result.build()

    def _get_colored_test_kind(self, kind: str) -> str:
        status_x_color_map = {
            str(TestKind.TEMPEST): self.palette.green(kind)
        }

        return status_x_color_map.get(
            kind,
            lambda: self.palette.underline(kind)
        )

    def _get_colored_test_result(self, result: str) -> str:
        status_x_color_map = {
            str(TestStatus.SUCCESS): self.palette.green(result),
            str(TestStatus.FAILURE): self.palette.red(result),
            str(TestStatus.SKIPPED): self.palette.blue(result)
        }

        return status_x_color_map.get(
            result,
            lambda: self.palette.underline(result)
        )
