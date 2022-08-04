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
from typing import NamedTuple

from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.output import QueryOutput, QueryOutputBuilderFactory


class SourceManager(ABC):
    """Base class for all handler that take care of performing the queries
    that a Zuul source receives.
    """

    class Tools(NamedTuple):
        """Tools this class uses to perform its task.
        """
        output: QueryOutputBuilderFactory = QueryOutputBuilderFactory()
        """Provides the tool used to generate the query output."""

    def __init__(self, api: Zuul, tools: Tools = Tools()):
        """Constructor.

        :param api: Interface with which to interact with the Zuul host.
            Must not be closed.
        :param tools: Tools this class uses to perform its task.
        """
        self._api = api
        self._tools = tools

    @property
    def api(self) -> Zuul:
        """
        :return: Interface this uses to interact with the Zuul host.
        """
        return self._api

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this class uses to perform its task.
        """
        return self._tools

    @abstractmethod
    def handle_tenants_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_projects_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_pipelines_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_jobs_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_variants_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_builds_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @abstractmethod
    def handle_tests_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError
