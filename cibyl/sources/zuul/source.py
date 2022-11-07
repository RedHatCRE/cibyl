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
from collections import UserDict
from dataclasses import dataclass, field
from typing import Iterable, List, MutableMapping

from overrides import overrides

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.server import ServerSource
from cibyl.sources.source import speed_index
from cibyl.sources.zuul.arguments import ArgumentReview
from cibyl.sources.zuul.output import QueryOutput
from cibyl.sources.zuul.queries.composition.factory import \
    AggregatedQueryFactory
from cibyl.sources.zuul.queries.modifiers.factory import QueryModifierFactory


class Zuul(ServerSource):
    """Source implementation for a Zuul host.
    """

    class Fallbacks(UserDict, MutableMapping[str, List[str]]):
        """Dictionary meant to hold the default search terms for arguments
        on a zuul query.

        Examples:
            >>> fallbacks = Zuul.Fallbacks()
            ... fallbacks['tenants'] = ['tenant_1', 'tenant_2']
            ... fallbacks['tenants']
            ['tenant_1', 'tenant_2']
        """

        @staticmethod
        def from_kwargs(keys: Iterable[str], **kwargs):
            result = Zuul.Fallbacks()

            for key in keys:
                if key not in kwargs:
                    continue

                result.update(kwargs[key])

            return result

    @dataclass
    class SourceSpec:
        name: str
        driver: str = field(default_factory=lambda *_: 'zuul')
        enabled: bool = field(default_factory=lambda *_: True)

    @dataclass
    class Tools:
        """Tools this uses to perform its task.
        """
        arguments: ArgumentReview = field(
            default_factory=lambda *_: ArgumentReview()
        )
        """Used to make sense out of the arguments coming from the user."""
        queries: AggregatedQueryFactory = field(
            default_factory=lambda *_: AggregatedQueryFactory()
        )
        """Used to generate the manager that will perform the query."""
        modifiers: QueryModifierFactory = field(
            default_factory=lambda *_: QueryModifierFactory()
        )
        """Used to extend queries for certain scenarios."""

    def __init__(self, provider, spec, fallbacks=None, tools=None):
        """Constructor.

        :param provider:
            Establishes the API this will use to interact with Zuul.
        :type provider:
            :class:`ZuulAPIFactory`
        :param spec:
            Common arguments that define the source for cibyl.
        :type spec:
            :class:`Zuul.SourceSpec`
        :param fallbacks:
            Default search terms to be used for missing query arguments.
            'None' to ignore.
        :type fallbacks:
            :class:`Zuul.Fallbacks` or None
        :param tools:
            Collection of tools this uses to do its task.
            'None' for defaults.
        :type tools:
            :class:`Zuul.Tools` or None
        """
        # Handle optional parameters
        if not fallbacks:
            fallbacks = Zuul.Fallbacks()

        if not tools:
            tools = Zuul.Tools()

        super().__init__(spec.name, spec.driver, enabled=spec.enabled)

        self._api = None

        self._provider = provider
        self._fallbacks = fallbacks
        self._tools = tools

    @property
    def tools(self):
        """
        :return: Collection of tools this uses to do its task.
        """
        return self._tools

    @overrides
    def setup(self):
        self._api = self._provider.new()

    @overrides
    def teardown(self):
        self._api.close()

    @speed_index({'base': 1})
    def get_tenants(self, **kwargs):
        """Retrieves tenants present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    @speed_index({'base': 2})
    def get_projects(self, **kwargs):
        """Retrieves projects present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    @speed_index({'base': 2})
    def get_pipelines(self, **kwargs):
        """Retrieves pipelines present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    @speed_index({'base': 3})
    def get_jobs(self, **kwargs):
        """Retrieves jobs present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    @speed_index({'base': 4})
    def get_builds(self, **kwargs):
        """Retrieves builds present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    @speed_index({'base': 5})
    def get_tests(self, **kwargs):
        """Retrieves tests present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed.
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self._handle_query(**kwargs)

    def _handle_query(self, **kwargs) -> AttributeDictValue:
        return AttributeDictValue(
            name='tenants',
            attr_type=Tenant,
            value=self._perform_query(defaults=self._fallbacks, **kwargs)
        )

    def _perform_query(self, **kwargs) -> QueryOutput:
        # Apply modifiers before performing the query
        modifiers = self.tools.modifiers.from_kwargs(self._api, **kwargs)

        for modifier in modifiers:
            kwargs = modifier.modify(**kwargs)

        # Perform the query
        query = self.tools.queries.from_kwargs(self._api, **kwargs)

        if self.tools.arguments.is_tenants_query_requested(**kwargs):
            query.with_tenants_query(**kwargs)

        if self.tools.arguments.is_projects_query_requested(**kwargs):
            query.with_projects_query(**kwargs)

        if self.tools.arguments.is_pipelines_query_requested(**kwargs):
            query.with_pipelines_query(**kwargs)

        if self.tools.arguments.is_jobs_query_requested(**kwargs):
            query.with_jobs_query(**kwargs)

        if self.tools.arguments.is_variants_query_requested(**kwargs):
            query.with_variants_query(**kwargs)

        if self.tools.arguments.is_builds_query_requested(**kwargs):
            query.with_builds_query(**kwargs)

        if self.tools.arguments.is_tests_query_requested(**kwargs):
            query.with_tests_query(**kwargs)

        return query.get_result()
