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
from cibyl.sources.zuul.queries.tenants import perform_query_for_tenants


def perform_query_for_projects(zuul, **kwargs):
    """Query for projects.

    :param zuul: API to interact with Zuul with.
    :type zuul: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved projects.
    :rtype: list[:class:`cibyl.sources.zuul.requests.ProjectResponse`]
    """
    result = []

    for tenant in perform_query_for_tenants(zuul, **kwargs):
        projects = tenant.projects()

        # Apply projects filters
        if 'projects' in kwargs:
            targets = kwargs['projects'].value

            # An empty '--projects' means all of them.
            if targets:
                projects.with_name(*targets)

        result += projects.get()

    return result
