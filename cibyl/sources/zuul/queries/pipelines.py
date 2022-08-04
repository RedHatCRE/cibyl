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
from cibyl.sources.zuul.queries.projects import perform_projects_query


def perform_pipelines_query(zuul, **kwargs):
    """Query for pipelines.

    :param zuul: API to interact with Zuul with.
    :type zuul: :class:`cibyl.sources.zuul.apis.ZuulAPI`
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved pipelines.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.PipelineResponse`]
    """
    result = []

    for project in perform_projects_query(zuul, **kwargs):
        pipelines = project.pipelines()

        # Apply pipelines filters
        if 'pipelines' in kwargs:
            targets = kwargs['pipelines'].value

            # An empty '--pipelines' means all of them.
            if targets:
                pipelines.with_name(*targets)

        result += pipelines.get()

    return result
