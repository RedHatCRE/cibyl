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

from cibyl.sources.zuul.queries.composition import AggregatedQuery


class VerboseQuery(AggregatedQuery):
    @overrides
    def with_tenants_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_projects_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_pipelines_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_jobs_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_variants_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_builds_query(self, **kwargs) -> 'AggregatedQuery':
        return self

    @overrides
    def with_tests_query(self, **kwargs) -> 'AggregatedQuery':
        return self
