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
from abc import ABC
from typing import Optional

from overrides import overrides

from cibyl.cli.output import OutputStyle
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.system import System
from cibyl.models.ci.zuul.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.models.ci.zuul.test import Test
from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.outputs.cli.ci.system.common.models import (get_plugin_section,
                                                       has_plugin_section)
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    SerializedBaseSystemPrinter
from cibyl.outputs.cli.printer import JSON, PROV, STDJSON


class SerializedZuulSystemPrinter(SerializedBaseSystemPrinter[PROV], ABC):
    """Base printer for all machine-readable printers dedicated to output
    Zuul systems.
    """

    @overrides
    def print_system(self, system: System) -> str:
        result = self.provider.load(super().print_system(system))

        if self.query >= QueryType.TENANTS:
            result['tenants'] = []

            for tenant in system.tenants.values():
                result['tenants'].append(
                    self.provider.load(
                        self.print_tenant(tenant)
                    )
                )

        return self.provider.dump(result)

    def print_tenant(self, tenant: Tenant) -> str:
        """
        :param tenant: The tenant.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': tenant.name.value,
            'projects': [],
            'jobs': []
        }

        for project in tenant.projects.values():
            result['projects'].append(
                self.provider.load(
                    self.print_project(project)
                )
            )

        for job in tenant.jobs.values():
            result['jobs'].append(
                self.provider.load(
                    self.print_job(job)
                )
            )

        return self.provider.dump(result)

    def print_project(self, project: Project) -> str:
        """
        :param project: The project.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': project.name.value,
            'url': project.url.value,
            'pipelines': []
        }

        for pipeline in project.pipelines.values():
            result['pipelines'].append(
                self.provider.load(
                    self.print_pipeline(pipeline)
                )
            )

        return self.provider.dump(result)

    def print_pipeline(self, pipeline: Pipeline) -> str:
        """
        :param pipeline: The pipeline.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': pipeline.name.value,
            'jobs': []
        }

        for job in pipeline.jobs.values():
            result['jobs'].append(
                {
                    'name': job.name.value
                }
            )

        return self.provider.dump(result)

    def print_job(self, job: Job) -> str:
        """
        :param job: The job.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': job.name.value,
            'url': job.url.value,
            'variants': [],
            'builds': []
        }

        for variant in job.variants:
            result['variants'].append(
                self.provider.load(
                    self.print_variant(variant)
                )
            )

        for build in job.builds.values():
            result['builds'].append(
                self.provider.load(
                    self.print_build(build)
                )
            )

        return self.provider.dump(result)

    def print_variant(self, variant: Job.Variant) -> str:
        """
        :param variant: The variant.
        :return: Textual representation of the provided model.
        """
        result = {
            'parent': variant.parent.value,
            'description': variant.description.value,
            'branches': variant.branches.value,
            'variables': variant.variables.value
        }

        return self.provider.dump(result)

    def print_build(self, build: Build) -> str:
        """
        :param build: The build.
        :return: Textual representation of the provided model.
        """
        result = {
            'uuid': build.build_id.value,
            'project': build.project.value,
            'pipeline': build.pipeline.value,
            'status': build.status.value,
            'duration': build.duration.value,
            'test_suites': []
        }

        for suite in build.suites:
            result['test_suites'].append(
                self.provider.load(
                    self.print_suite(suite)
                )
            )

        return self.provider.dump(result)

    def print_suite(self, suite: TestSuite) -> str:
        """
        :param suite: The suite.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': suite.name.value,
            'url': suite.url.value,
            'test_count': suite.test_count,
            'succeeded': suite.success_count,
            'failed': suite.failed_count,
            'skipped': suite.skipped_count,
            'tests': []
        }

        for test in suite.tests:
            result['tests'].append(
                self.provider.load(
                    self.print_test(test)
                )
            )

        return self.provider.dump(result)

    def print_test(self, test: Test) -> str:
        """
        :param test: The test.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': test.name.value,
            'type': test.kind.value,
            'duration': test.duration.value,
            'result': test.result.value,
            'url': test.url.value
        }

        return self.provider.dump(result)


class JSONZuulSystemPrinter(SerializedZuulSystemPrinter[JSON]):
    """Printer that will output Zuul system in JSON format.
    """

    def __init__(
        self,
        provider: Optional[JSON] = None,
        query: QueryType = QueryType.NONE,
        verbosity: int = 0
    ):
        """Constructor. See parent for more information.

        :param provider: Implementation of a JSON marshaller / unmarshaller.
            Leave as 'None' to let this build its own.
        """
        if provider is None:
            provider = STDJSON()

        super().__init__(provider, query, verbosity)

    @overrides
    def print_variant(self, variant: Job.Variant) -> str:
        result = self.provider.load(super().print_variant(variant))

        if has_plugin_section(variant):
            section = self.provider.load(
                get_plugin_section(
                    style=OutputStyle.JSON,
                    model=variant,
                    reference=self
                )
            )

            result['plugins'] = section

        return self.provider.dump(result)
