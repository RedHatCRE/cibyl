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
from cibyl.sources.zuul.queries.tenants import perform_tenants_query


def perform_jobs_query(zuul, **kwargs):
    """Query for jobs.

    :param zuul: API to interact with Zuul with.
    :type zuul: :class:`cibyl.sources.zuul.apis.ZuulAPI`
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved jobs.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.JobResponse`]
    """
    result = []

    for tenant in perform_tenants_query(zuul, **kwargs):
        jobs = tenant.jobs()

        # Apply jobs filters
        if 'jobs' in kwargs:
            targets = kwargs['jobs'].value

            # An empty '--jobs' means all of them.
            if targets:
                jobs.with_name(*targets)

        result += jobs.get()

    return result
