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
from enum import IntEnum

from cibyl.utils.dicts import subset


class QueryType(IntEnum):
    """Defines the hierarchy level at which a query is meant to be performed.
    """
    NONE = 0
    """No data from host is requested."""
    TENANTS = 1
    """Only retrieve data concerning tenants."""
    PROJECTS = 2
    """Retrieve data concerning projects and above."""
    PIPELINES = 3
    """Retrieve data concerning pipelines and above."""
    JOBS = 4
    """Retrieve data concerning jobs and above."""
    BUILDS = 5
    """Retrieve data concerning builds and above."""


class QuerySelector:
    """Deduce the type of query performed from the cli argument considering
    both core argument and plugin provided ones."""
    query_selector_functions = []

    def get_query_type_core(self, **kwargs):
        """Deduces the type of query from a set of arguments related to cibyl
        core ci models.

        :param kwargs: The arguments.
        :key tenants: Query targets tenants.
        :key projects: Query targets projects.
        :key pipelines: Query targets pipelines.
        :key jobs: Query targets jobs.
        :key builds: Query target builds.
        :return: The lowest query level possible. For example,
            if both 'tenants' and 'builds' are requested, this will choose
            'builds' over 'tenants'.
        :rtype: :class:`QueryType`
        """

        result = QueryType.NONE

        if 'tenants' in kwargs:
            result = QueryType.TENANTS

        if 'projects' in kwargs:
            result = QueryType.PROJECTS

        if 'pipelines' in kwargs:
            result = QueryType.PIPELINES

        job_args = subset(kwargs, ["jobs", "variants", "job_url"])
        if job_args:
            result = QueryType.JOBS

        build_args = subset(kwargs, ["builds", "last_build", "build_status"])
        if build_args:
            result = QueryType.BUILDS

        return result

    def get_type_query(self, **kwargs):
        """Deduce the type of query from the given arguments, taking into
        account arguments provided by the plugins, if present. It will return
        the largest query type provided by either the core types or the
        plugins."""
        core_query = self.get_query_type_core(**kwargs)
        plugins_query = QueryType.NONE
        if self.query_selector_functions:
            plugins_query = max([get_query(**kwargs) for get_query in
                                 self.query_selector_functions])
        return max(core_query, plugins_query)


def get_query_type(**kwargs):
    """Deduces the type of query from a set of arguments.

    :param kwargs: The arguments.
    :key tenants: Query targets tenants.
    :key projects: Query targets projects.
    :key pipelines: Query targets pipelines.
    :key jobs: Query targets jobs.
    :key builds: Query target builds.
    :return: The lowest query level possible. For example,
        if both 'tenants' and 'builds' are requested, this will choose
        'builds' over 'tenants'.
    :rtype: :class:`QueryType`
    """
    query_selector = QuerySelector()
    return query_selector.get_type_query(**kwargs)
