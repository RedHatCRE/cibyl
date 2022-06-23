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

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.system.impls.base.serialized import \
    JSONBaseSystemPrinter


class JSONJobsSystemPrinter(JSONBaseSystemPrinter):
    @overrides
    def print_system(self, system):
        # Build on top of the base answer
        result = self._load(super().print_system(system))

        if self.query != QueryType.NONE:
            result['jobs'] = []

            for job in system.jobs.values():
                result['jobs'].append(self._load(self.print_job(job)))

        return self._dump(result)

    def print_job(self, job):
        result = {
            'name': job.name.value
        }

        if self.query in (QueryType.FEATURES_JOBS, QueryType.FEATURES):
            return self._dump(result)

        if self.query >= QueryType.BUILDS:
            result['builds'] = []

            for build in job.builds.values():
                result['builds'].append(self._load(self.print_build(build)))

        return self._dump(result)

    def print_build(self, build):
        result = {
            'uuid': build.build_id.value,
            'status': build.status.value,
            'duration': build.duration.value,
            'tests': [],
            'stages': []
        }

        for test in build.tests.values():
            result['tests'].append(self._load(self.print_test(test)))

        for stage in build.stages:
            result['stages'].append(self._load(self.print_stage(stage)))

        return self._dump(result)

    def print_test(self, test):
        result = {
            'name': test.name.value,
            'result': test.result.value,
            'class_name': test.class_name.value,
            'duration': test.duration.value
        }

        return self._dump(result)

    def print_stage(self, stage):
        result = {
            'name': stage.name.value,
            'status': stage.status.value,
            'duration': stage.duration.value
        }

        return self._dump(result)
