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


def perform_builds_query(job, **kwargs):
    """Query for builds.

    :param job: API to interact with the owner of the builds.
    :type job: :class:`cibyl.sources.zuul.transactions.JobResponse`
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved builds.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.BuildResponse`]
    """
    result = []

    builds = job.builds()

    # Apply builds filters
    if 'builds' in kwargs:
        targets = kwargs['builds'].value

        # An empty '--builds' means all of them.
        if targets:
            builds.with_uuid(*targets)

    if 'projects' in kwargs:
        targets = kwargs['projects'].value

        # An empty '--projects' means all of them.
        if targets:
            builds.with_project(*targets)

    if 'pipelines' in kwargs:
        targets = kwargs['pipelines'].value

        # An empty '--pipelines' means all of them.
        if targets:
            builds.with_pipeline(*targets)

    if 'build_status' in kwargs:
        builds.with_status(*kwargs['build_status'].value)

    if 'last_build' in kwargs:
        builds.with_last_build_only()

    result += builds.get()

    return result
