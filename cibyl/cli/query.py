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
from enum import Enum


class QueryType(Enum):
    """Defines the hierarchy level at which a query is meant to be performed.
    """
    NONE = 0
    """No data from host is requested."""
    TENANTS = 1
    """Only retrieve data concerning tenants."""
    JOBS = 2
    """Retrieve data concerning jobs and above."""
    BUILDS = 3
    """Retrieve data concerning builds and above."""


def get_query_type(**kwargs):
    """Deduces the type of query from a set of arguments.

    :param kwargs: The arguments.
    :key tenants: Query targets tenants.
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

    if 'jobs' in kwargs:
        result = QueryType.JOBS

    if 'builds' in kwargs:
        result = QueryType.BUILDS

    return result
