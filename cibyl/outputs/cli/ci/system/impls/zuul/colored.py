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
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.system import System
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.models.ci.zuul.test import Test, TestStatus, TestKind
from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.outputs.cli.ci.system.common.builds import (get_duration_section,
                                                       get_status_section)
from cibyl.outputs.cli.ci.system.common.models import (get_plugin_section,
                                                       has_plugin_section)
from cibyl.outputs.cli.ci.system.impls.base.colored import \
    ColoredBaseSystemPrinter
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.filtering import apply_filters
from cibyl.utils.sorting import sort
from cibyl.utils.strings import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColoredZuulSystemPrinter(ColoredBaseSystemPrinter):
    """Printer meant for :class:`ZuulSystem`, decorated with colors for
    easier read.
    """

    class ProjectCascade(ColoredPrinter):
        """Printer meant for :class:`Project` and all of its children. This
        printer focuses more on providing a high-level view of the
        relationship between elements more than their details.
        """

        def print_project(self, project: Project) -> str:
            result = IndentedTextBuilder()

            result.add(self.palette.blue('Project: '), 0)
            result[-1].append(project.name)

            if self.verbosity > 0:
                result.add(self.palette.blue('URL: '), 1)
                result[-1].append(project.url)

            if self.query >= QueryType.PIPELINES:
                if project.pipelines.value:
                    for pipeline in project.pipelines.values():
                        result.add(self.print_pipeline(project, pipeline), 1)

                    msg = "Total pipelines found in query for project '"
                    result.add(self.palette.blue(msg), 1)
                    result[-1].append(self.palette.underline(project.name))
                    result[-1].append(self.palette.blue("': "))
                    result[-1].append(len(project.pipelines))
                else:
                    msg = 'No pipelines found in query.'
                    result.add(self.palette.red(msg), 1)

            return result.build()

        def print_pipeline(self, project: Project, pipeline: Pipeline) -> str:
            result = IndentedTextBuilder()

            result.add(self.palette.blue('Pipeline: '), 0)
            result[-1].append(pipeline.name)

            if self.query >= QueryType.JOBS:
                if pipeline.jobs.value:
                    for job in pipeline.jobs.values():
                        result.add(self.print_job(project, pipeline, job), 1)

                    msg = "Total jobs found in query for pipeline '"
                    result.add(self.palette.blue(msg), 1)
                    result[-1].append(self.palette.underline(pipeline.name))
                    result[-1].append(self.palette.blue("': "))
                    result[-1].append(len(pipeline.jobs))
                else:
                    msg = 'No jobs found in query.'
                    result.add(self.palette.red(msg), 1)

            return result.build()

        def print_job(self, project: Project, pipeline: Pipeline,
                      job: Job) -> str:
            result = IndentedTextBuilder()

            result.add(self.palette.blue('Job: '), 0)
            result[-1].append(job.name.value)

            if self.query >= QueryType.BUILDS:
                builds = apply_filters(
                    job.builds.values(),
                    lambda bld: bld.project.value != project.name.value,
                    lambda bld: bld.pipeline.value != pipeline.name.value
                )

                if builds:
                    for build in builds:
                        msg = self.print_build(project, pipeline, job, build)
                        result.add(msg, 1)
                else:
                    msg = 'No builds in query.'
                    result.add(self.palette.red(msg), 1)

            return result.build()

        def print_build(self, project: Project, pipeline: Pipeline, job: Job,
                        build: Build) -> str:
            result = IndentedTextBuilder()

            result.add(self.palette.blue('Build: '), 1)
            result[-1].append(build.build_id.value)

            if build.status.value:
                result.add(get_status_section(self.palette, build), 2)

            return result.build()

    class JobCascade(ColoredPrinter):
        """Printer meant for :class:`Job` and all of its children. This
        printer focused on giving as much information as possible on each
        element.
        """

        def print_job(self, job: Job) -> str:
            result = IndentedTextBuilder()

            result.add(self.palette.blue('Job: '), 0)
            result[-1].append(job.name.value)

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
                result.add(get_plugin_section(self, variant), 1)

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

                for suite in build.suites:
                    result.add(self.print_suite(suite), 2)

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
                result[-1].append(test.duration.value)

            result.add(self.palette.blue('Result: '), 1)
            result[-1].append(self._get_colored_test_result(test.result.value))

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

    @overrides
    def print_system(self, system: System) -> str:
        printer = IndentedTextBuilder()

        # Begin with the text common to all systems
        printer.add(super().print_system(system), 0)

        if self.query == QueryType.FEATURES:
            # if the user has only requested features, there is no need to
            # print anything else
            return printer.build()
        # Continue with text specific for this system type
        if self.query >= QueryType.TENANTS:
            if hasattr(system, 'tenants'):
                if not system.is_queried():
                    msg = 'No query performed.'
                    printer.add(self.palette.blue(msg), 1)
                elif system.tenants.value:
                    for tenant in system.tenants.values():
                        printer.add(self.print_tenant(tenant), 1)

                    header = 'Total tenants found in query: '
                    printer.add(self.palette.blue(header), 1)
                    printer[-1].append(len(system.tenants))
                else:
                    msg = 'No tenants found in query.'
                    printer.add(self.palette.red(msg), 1)
            else:
                LOG.warning(
                    'Requested tenant printing on a non-zuul interface. '
                    'Ignoring...'
                )

        return printer.build()

    def print_tenant(self, tenant: Tenant) -> str:
        """
        :param tenant: The tenant.
        :return: Textual representation of the provided model.
        """

        def print_projects() -> None:
            def create_printer() -> ColoredZuulSystemPrinter.ProjectCascade:
                return ColoredZuulSystemPrinter.ProjectCascade(
                    self.query, self.verbosity, self.palette
                )

            # Avoid header if there are no project
            result.add(self.palette.blue('Projects: '), 1)

            if tenant.projects.value:
                for project in tenant.projects.values():
                    result.add(create_printer().print_project(project), 2)

                result.add(
                    self.palette.blue(
                        "Total projects found in query for tenant '"
                    ), 1
                )
                result[-1].append(self.palette.underline(tenant.name))
                result[-1].append(self.palette.blue("': "))
                result[-1].append(len(tenant.projects))
            else:
                msg = 'No projects found in query.'
                result.add(self.palette.red(msg), 2)

        def print_jobs() -> None:
            def create_printer() -> ColoredZuulSystemPrinter.JobCascade:
                return ColoredZuulSystemPrinter.JobCascade(
                    self.query, self.verbosity, self.palette
                )

            # Avoid header if there are no jobs
            result.add(self.palette.blue('Jobs: '), 1)

            if tenant.jobs.value:
                for job in sort(tenant.jobs.values(), self._job_sorter):
                    result.add(create_printer().print_job(job), 2)

                result.add(
                    self.palette.blue(
                        "Total jobs found in query for tenant '"
                    ), 1
                )

                result[-1].append(self.palette.underline(tenant.name))
                result[-1].append(self.palette.blue("': "))
                result[-1].append(len(tenant.jobs))
            else:
                msg = 'No jobs found in query.'
                result.add(self.palette.red(msg), 2)

        result = IndentedTextBuilder()

        result.add(self.palette.blue('Tenant: '), 0)
        result[-1].append(tenant.name)

        if self.query >= QueryType.PROJECTS:
            print_projects()

            if self.query >= QueryType.JOBS:
                print_jobs()

        return result.build()
