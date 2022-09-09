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
from cibyl.models.ci.base.build import Build, Test
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.stage import Stage
from cibyl.models.ci.base.system import System
from cibyl.outputs.cli.ci.system.common.features import is_features_query
from cibyl.outputs.cli.ci.system.common.models import (get_plugin_section,
                                                       has_plugin_section)
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    SerializedBaseSystemPrinter
from cibyl.outputs.cli.printer import JSON, PROV, STDJSON


class SerializedJobsSystemPrinter(SerializedBaseSystemPrinter[PROV], ABC):
    """Base printer for all machine-readable printers dedicated to output
    Jenkins systems.
    """

    @overrides
    def print_system(self, system: System) -> str:
        # Build on top of the base answer
        result = self.provider.load(super().print_system(system))

        if self.query != QueryType.NONE:
            result['jobs'] = []

            for job in system.jobs.values():
                result['jobs'].append(
                    self.provider.load(
                        self.print_job(job)
                    )
                )

        return self.provider.dump(result)

    def print_job(self, job: Job) -> str:
        """
        :param job: The job.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': job.name.value
        }

        if is_features_query(self.query):
            return self.provider.dump(result)

        if self.query >= QueryType.BUILDS:
            result['builds'] = []

            for build in job.builds.values():
                result['builds'].append(
                    self.provider.load(
                        self.print_build(build)
                    )
                )

        return self.provider.dump(result)

    def print_build(self, build: Build) -> str:
        """
        :param build: The build.
        :return: Textual representation of the provided model.
        """
        result = {
            'uuid': build.build_id.value,
            'status': build.status.value,
            'duration': build.duration.value,
            'tests': [],
            'stages': []
        }

        for test in build.tests.values():
            result['tests'].append(
                self.provider.load(
                    self.print_test(test)
                )
            )

        for stage in build.stages:
            result['stages'].append(
                self.provider.load(
                    self.print_stage(stage)
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
            'result': test.result.value,
            'class_name': test.class_name.value,
            'duration': test.duration.value
        }

        return self.provider.dump(result)

    def print_stage(self, stage: Stage) -> str:
        """
        :param stage: The stage.
        :return: Textual representation of the provided model.
        """
        result = {
            'name': stage.name.value,
            'status': stage.status.value,
            'duration': stage.duration.value
        }

        return self.provider.dump(result)


class JSONJobsSystemPrinter(SerializedJobsSystemPrinter[JSON]):
    """Printer that will output Jenkins systems in JSON format.
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
    def print_job(self, job: Job) -> str:
        result = self.provider.load(super().print_job(job))

        if has_plugin_section(job):
            section = self.provider.load(
                get_plugin_section(
                    style=OutputStyle.JSON,
                    model=job,
                    reference=self
                )
            )

            result['plugins'] = section

        return self.provider.dump(result)
