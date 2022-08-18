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

from cibyl.sources.zuul.queries.builds import perform_builds_query
from cibyl.sources.zuul.queries.composition import AggregatedQuery
from cibyl.sources.zuul.queries.jobs import perform_jobs_query
from cibyl.sources.zuul.queries.pipelines import perform_pipelines_query
from cibyl.sources.zuul.queries.projects import perform_projects_query
from cibyl.sources.zuul.queries.tenants import perform_tenants_query
from cibyl.sources.zuul.queries.tests import perform_tests_query
from cibyl.sources.zuul.queries.variants import perform_variants_query


class QuickQuery(AggregatedQuery):
    """A kind of complex query that focuses on speed over completeness.
    """

    @overrides
    def with_tenants_query(self, **kwargs) -> 'AggregatedQuery':
        for tenant in perform_tenants_query(self.api, **kwargs):
            self.tools.builder.with_tenant(tenant)

        return self

    @overrides
    def with_projects_query(self, **kwargs) -> 'AggregatedQuery':
        for project in perform_projects_query(self.api, **kwargs):
            self.tools.builder.with_project(project)

        return self

    @overrides
    def with_pipelines_query(self, **kwargs) -> 'AggregatedQuery':
        for pipeline in perform_pipelines_query(self.api, **kwargs):
            self.tools.builder.with_pipeline(pipeline)

        return self

    @overrides
    def with_jobs_query(self, **kwargs) -> 'AggregatedQuery':
        for job in perform_jobs_query(self.api, **kwargs):
            self.tools.builder.with_job(job)

        return self

    @overrides
    def with_variants_query(self, **kwargs) -> 'AggregatedQuery':
        for job in perform_jobs_query(self.api, **kwargs):
            for variant in perform_variants_query(job, **kwargs):
                self.tools.builder.with_variant(variant)

        return self

    @overrides
    def with_builds_query(self, **kwargs) -> 'AggregatedQuery':
        for job in perform_jobs_query(self.api, **kwargs):
            for build in perform_builds_query(job, **kwargs):
                self.tools.builder.with_build(build)

        return self

    @overrides
    def with_tests_query(self, **kwargs) -> 'AggregatedQuery':
        for job in perform_jobs_query(self.api, **kwargs):
            for build in perform_builds_query(job, **kwargs):
                for test in perform_tests_query(build, **kwargs):
                    self.tools.builder.with_test(test)

        return self
