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
    """Represents a query whose result is composed of the result of others.

    When a simple query is not enough to satisfy the demands from the user,
    this class can be used to generate a more complex response from the
    answer of those queries. Output produced here is done from the
    merging of the models retrieved from all the other calls. No data is
    duplicated, but instead each new call adds up to the output. Access to
    each of the known atomic queries is provided in the format of a builder
    class.
    """

    def __init__(self, api: Zuul):
        """Constructor.

        :param api: Low-Level API with which to communicate with the Zuul host.
        """
        self._api = api
        self._result = QueryOutputBuilder()

    @property
    def api(self) -> Zuul:
        """
        :return: Low-Level API with which to communicate with the Zuul host.
        """
        return self._api

    @abstractmethod
    def with_tenants_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the tenants' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_projects_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the projects' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_pipelines_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the pipelines' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_jobs_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the jobs' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_variants_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the variants' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_builds_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the builds' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    @abstractmethod
    def with_tests_query(self, **kwargs) -> 'AggregatedQuery':
        """Calls and adds the result of the tests' query to this.

        :param kwargs: Arguments received from the command line.
        :return: The query's instance.
        """
        raise NotImplementedError

    def get_result(self) -> QueryOutput:
        """
        :return: Result of the complex query.
        """
        return self._result.assemble()
