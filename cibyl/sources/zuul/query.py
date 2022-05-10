"""Retrieval of data from a Zuul host in a format that Cibyl can use and
understand.

License:
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
import logging

from cibyl.cli.query import QueryType, get_query_type
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.zuul.models import ModelBuilder
from cibyl.sources.zuul.requests import TenantsRequest

LOG = logging.getLogger(__name__)


def _get_builds(zuul, **kwargs):
    """Query for builds.

    :param zuul: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved builds.
    :rtype: list[:class:`cibyl.sources.zuul.requests.BuildResponse`]
    """
    result = []

    for job in _get_jobs(zuul, **kwargs):
        builds = job.builds()

        # Apply builds filters
        if 'builds' in kwargs:
            targets = kwargs['builds'].value

            # An empty '--builds' means all of them.
            if targets:
                builds.with_uuid(*targets)

        if 'build_status' in kwargs:
            builds.with_status(*kwargs['build_status'].value)

        if 'last_build' in kwargs:
            builds.with_last_build_only()

        result += builds.get()

    return result


def _get_jobs(zuul, **kwargs):
    """Query for jobs.

    :param zuul: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved jobs.
    :rtype: list[:class:`cibyl.sources.zuul.requests.JobResponse`]
    """
    result = []

    for tenant in _get_tenants(zuul, **kwargs):
        # TODO: Fetch jobs in projects

        jobs = tenant.jobs()

        # Apply jobs filters
        if 'jobs' in kwargs:
            targets = kwargs['jobs'].value

            # An empty '--jobs' means all of them.
            if targets:
                jobs.with_name(*targets)

        if 'job_url' in kwargs:
            jobs.with_url(*kwargs['job_url'].value)

        result += jobs.get()

    return result


def _get_pipelines(zuul, **kwargs):
    """Query for pipelines.

    :param zuul: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved pipelines.
    :rtype: list[:class:`cibyl.sources.zuul.requests.PipelineResponse`]
    """
    result = []

    for project in _get_projects(zuul, **kwargs):
        pipelines = project.pipelines()

        # Apply pipelines filters
        if 'pipelines' in kwargs:
            targets = kwargs['pipelines'].value

            # An empty '--pipelines' means all of them.
            if targets:
                pipelines.with_name(*targets)

        result += pipelines.get()

    return result


def _get_projects(zuul, **kwargs):
    """Query for projects.

    :param zuul: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved projects.
    :rtype: list[:class:`cibyl.sources.zuul.requests.ProjectResponse`]
    """
    result = []

    for tenant in _get_tenants(zuul, **kwargs):
        projects = tenant.projects()

        # Apply projects filters
        if 'projects' in kwargs:
            targets = kwargs['projects'].value

            # An empty '--projects' means all of them.
            if targets:
                projects.with_name(*targets)

        result += projects.get()

    return result


def _get_tenants(zuul, **kwargs):
    """Query for tenants.

    :param zuul: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved tenants.
    :rtype: list[:class:`cibyl.sources.zuul.requests.TenantResponse`]
    """

    def by_name_filter():
        # Check CLI arguments
        if 'tenants' in kwargs:
            targets = kwargs['tenants'].value

            # An empty '--tenants' means all of them.
            if targets:
                tenants.with_name(*targets)
        else:
            # Check configuration file
            if 'defaults' in kwargs:
                defaults = kwargs['defaults']

                if 'tenants' in defaults:
                    targets = defaults['tenants']

                    # An empty 'tenants: ' means none of them.
                    if not targets:
                        LOG.warning('No tenants selected for query. '
                                    'Please check your configuration file.')

                    tenants.with_name(*targets)

    tenants = TenantsRequest(zuul)

    # Apply tenants filters
    by_name_filter()

    return tenants.get()


def handle_query(api, **kwargs):
    """Generates and performs a query on a Zuul host based on the given
    arguments.

    :param api: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
    :param kwargs: Arguments that define the query that will be performed.
        If one of these keys is not present, it is simply ignored.
    :key defaults:
        Dictionary with the default search terms in case an argument is
        omitted. Type: Zuul.Fallbacks.
    :key tenants:
        Name of the tenants to query. Type: AttributeListValue[str].
    :key jobs:
        Name of the jobs to query. Type: AttributeListValue[str].
    :key job_url:
        URL of the jobs to query. Type: AttributeListValue[str].
    :key builds:
        Name of the builds to query. Type: AttributeListValue[str].
    :key builds_status:
        Status of the builds to query. Type: AttributeListValue[str].
    :key last_build:
        Will only return the newest build from the query. Type: None.
    :return: Attribute assembled for usage by Cibyl.
    :rtype: :class:`AttributeDictValue`
    """
    model = ModelBuilder()
    query = get_query_type(**kwargs)

    if query == QueryType.TENANTS:
        for tenant in _get_tenants(api, **kwargs):
            model.with_tenant(tenant)

    if query == QueryType.PROJECTS:
        for project in _get_projects(api, **kwargs):
            model.with_project(project)

    if query == QueryType.PIPELINES:
        for pipeline in _get_pipelines(api, **kwargs):
            model.with_pipeline(pipeline)

    if query == QueryType.JOBS:
        pipelines = _get_pipelines(api, **kwargs)

        for job in _get_jobs(api, **kwargs):
            job_model = model.with_job(job)

            # Include also the pipelines where this job is present
            for pipeline in pipelines:
                pipeline_jobs = [j.name for j in pipeline.jobs().get()]

                # Is the job on this pipeline?
                if job.name in pipeline_jobs:
                    pipeline_model = model.with_pipeline(pipeline)
                    pipeline_model.add_job(job_model)

            # Check if the user requested variants
            if 'variants' in kwargs:
                for variant in job.variants().get():
                    job_model.add_variant(
                        Job.Variant(
                            variant.data['parent'],
                            variant.data['description'],
                            variant.data['branches'],
                            variant.data['variables']
                        )
                    )

    if query == QueryType.BUILDS:
        for build in _get_builds(api, **kwargs):
            model.with_build(build)

    # Format the result
    return AttributeDictValue(
        name='tenants',
        attr_type=Tenant,
        value=model.assemble()
    )
