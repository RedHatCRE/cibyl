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
from typing import List, MutableMapping, NamedTuple, Optional

from overrides import overrides

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.server import ServerSource
from cibyl.sources.source import speed_index
from cibyl.sources.zuul.apis.factories import ZuulAPIFactory
from cibyl.sources.zuul.apis.factories.rest import ZuulRESTFactory
from cibyl.sources.zuul.arguments import ArgumentReview
from cibyl.sources.zuul.output import QueryOutput
from cibyl.sources.zuul.queries.composition.factory import \
    AggregatedQueryFactory
from cibyl.utils.dicts import subset


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

    class Tools(NamedTuple):
        """Tools this uses to perform its task.
        """
        api: ZuulAPIFactory
        """Used to get the API this will use to interact with Zuul."""
        arguments: ArgumentReview
        """Used to make sense out of the arguments coming from the user."""
        query: AggregatedQueryFactory
        """Used to generate the manager that will perform the query."""

    def __init__(self, name, driver, url, cert=None,
                 fallbacks=None, tenants=None, enabled=True,
                 tools: Optional[Tools] = None):
        """Constructor.

        :param name: Name of the source.
        :type name: str
        :param driver: Driver used by the source.
        :type driver: str
        :param url: Address where the host is located.
        :type url: str
        :param cert: See :meth:`ZuulRESTClient.from_url`
        :type cert: str or None
        :param fallbacks: Default search terms to be used for missing query
            arguments.
        :type fallbacks: :class:`Zuul.Fallbacks` or None
        :param tenants: List of tenants
        :type tenants: list
        :param tools: Collection of tools this uses to do its task.
            'None' for defaults.
        :type tools: :class:`Zuul.Tools`
        """
        # Handle optional parameters
        if not fallbacks:
            fallbacks = Zuul.Fallbacks()

        if not tools:
            tools = Zuul.Tools(
                api=ZuulRESTFactory(),
                arguments=ArgumentReview(),
                query=AggregatedQueryFactory()
            )

        # URLs are built assuming no slash at the end of URL
        if url.endswith('/'):
            url = url[:-1]  # Removes last character of string

        super().__init__(name, driver, url=url, cert=cert, enabled=enabled)

        self._api = None

        self._fallbacks = fallbacks
        self._tenants = tenants
        self._tools = tools

    @staticmethod
    def new_source(url, cert=None, **kwargs):
        """Builds a Zuul source from the data that describes it.

        :param url: Address of Zuul's host.
        :type url: str
        :param cert: See :meth:`ZuulRESTClient.from_url`
        :type cert: str or None
        :key name:
            Name of the source.
            Type: str. Default: 'zuul-ci'.
        :key driver:
            Driver for this source.
            Type: str. Default: 'zuul'.
        :key priority:
            Priority of the source.
            Type: int. Default: 0.
        :key enabled:
            Whether this source is to be used.
            Type: bool. Default: True.
        :return: The instance.
        """

        def new_fallbacks_from(*args):
            """
            :param args: Arguments to generate fallbacks for.
            :return: Dictionary with the default values of the requested
                arguments.
            :rtype: :class:`Zuul.Fallbacks`
            """
            result = Zuul.Fallbacks()

            for entry in args:
                if entry in kwargs:
                    # Add the default values for this entry
                    result.update(subset(kwargs, [entry]))

            return result

        kwargs.setdefault('name', 'zuul-ci')
        kwargs.setdefault('driver', 'zuul')

        fallbacks = new_fallbacks_from('tenants')

        return Zuul(url=url, cert=cert, fallbacks=fallbacks, **kwargs)

    @property
    def tools(self):
        """
        :return: Collection of tools this uses to do its task.
        """
        return self._tools

    @overrides
    def setup(self):
        self._api = self.tools.api.create(self.url, self.cert)

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
        query = self.tools.query.from_kwargs(self._api, **kwargs)

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
