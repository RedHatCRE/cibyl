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
from dataclasses import dataclass, field
from typing import Optional

from overrides import overrides

from cibyl.cli.argument import Argument
from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.arguments import ArgumentReview
from cibyl.sources.zuul.queries.jobs import perform_jobs_query
from cibyl.sources.zuul.queries.modifiers import Query, QueryModifier
from cibyl.sources.zuul.queries.variants import perform_variants_query
from cibyl.sources.zuul.utils.variants.hierarchy import HierarchyCrawlerFactory


class HierarchyModifier(QueryModifier):
    """Adds enough arguments to a query so that it is possible to later
    calculate the hierarchy of jobs fetched by the query.
    """

    @dataclass
    class Tools:
        """Tools this uses to do its job.
        """
        arguments: ArgumentReview = field(
            default_factory=lambda: ArgumentReview()
        )
        """Tool used to interpret arguments on the query."""
        crawlers: HierarchyCrawlerFactory = field(
            default_factory=lambda: HierarchyCrawlerFactory()
        )
        """Tools used to iterate through a job's hierarchy."""

    def __init__(self, api: Zuul, tools: Optional[Tools] = None):
        """Constructor.

        :param api: Channel of communication with the Zuul host.
        :param tools: Tools this uses to do its task.
        """
        if tools is None:
            tools = HierarchyModifier.Tools()

        self._api = api
        self._tools = tools

    @property
    def api(self) -> Zuul:
        """
        :return: Channel of communication with the Zuul host.
        """
        return self._api

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its task.
        """
        return self._tools

    @overrides
    def modify(self, **kwargs) -> Query:
        if not self.tools.arguments.is_jobs_query_requested(**kwargs):
            return kwargs

        if 'jobs' not in kwargs:
            kwargs.update(
                {
                    'jobs': Argument(
                        name='jobs',
                        arg_type=str,
                        description='',
                        nargs='*',
                        value=[]
                    )
                }
            )

        if 'variants' not in kwargs:
            kwargs.update(
                {
                    'variants': Argument(
                        name='variant',
                        arg_type=str,
                        description='',
                        nargs=0,
                        value=[]
                    )
                }
            )

        for job in perform_jobs_query(self.api, **kwargs):
            for variant in perform_variants_query(job, **kwargs):
                crawler = self.tools.crawlers.from_variant(variant)

                for level in crawler:
                    kwargs['jobs'].value.append(f'^{level.name}$')

        return kwargs
