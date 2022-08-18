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
from abc import ABC, abstractmethod

from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.output import QueryOutput, QueryOutputBuilder


class AggregatedQuery(ABC):
    def __init__(self, api: Zuul):
        self._api = api
        self._result = QueryOutputBuilder()

    @property
    def api(self):
        return self._api

    @abstractmethod
    def with_tenants_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_projects_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_pipelines_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_jobs_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_variants_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_builds_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    @abstractmethod
    def with_tests_query(self, **kwargs) -> 'AggregatedQuery':
        raise NotImplementedError

    def get_result(self) -> QueryOutput:
        return self._result.assemble()
