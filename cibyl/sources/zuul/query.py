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
from cibyl.sources.zuul.models import ModelBuilder
from cibyl.sources.zuul.queries.builds import perform_query_for_builds
from cibyl.sources.zuul.queries.jobs import perform_query_for_jobs
from cibyl.sources.zuul.queries.pipelines import perform_query_for_pipelines
from cibyl.sources.zuul.queries.projects import perform_query_for_projects
from cibyl.sources.zuul.queries.tenants import perform_query_for_tenants
from cibyl.sources.zuul.queries.variants import perform_query_for_variants

LOG = logging.getLogger(__name__)


def _handle_tenants_query(zuul, **kwargs):
    model = ModelBuilder()

    for tenant in perform_query_for_tenants(zuul, **kwargs):
        model.with_tenant(tenant)

    return model


def _handle_projects_query(zuul, **kwargs):
    model = ModelBuilder()

    if 'tenants' in kwargs:
        for tenant in perform_query_for_tenants(zuul, **kwargs):
            model.with_tenant(tenant)

    for project in perform_query_for_projects(zuul, **kwargs):
        model.with_project(project)

    return model


def _handle_pipelines_query(zuul, **kwargs):
    model = ModelBuilder()

    if 'tenants' in kwargs:
        for tenant in perform_query_for_tenants(zuul, **kwargs):
            model.with_tenant(tenant)

    if 'projects' in kwargs:
        for project in perform_query_for_projects(zuul, **kwargs):
            model.with_project(project)

    for pipeline in perform_query_for_pipelines(zuul, **kwargs):
        model.with_pipeline(pipeline)

    return model


def _handle_jobs_query(zuul, **kwargs):
    def get_pipeline_jobs():
        return [j.name for j in pipeline.jobs().get()]

    model = ModelBuilder()

    if 'tenants' in kwargs:
        for tenant in perform_query_for_tenants(zuul, **kwargs):
            model.with_tenant(tenant)

    if 'projects' in kwargs:
        for project in perform_query_for_projects(zuul, **kwargs):
            model.with_project(project)

    pipelines = perform_query_for_pipelines(zuul, **kwargs)

    if 'pipelines' in kwargs:
        for pipeline in pipelines:
            model.with_pipeline(pipeline)

    jobs = perform_query_for_jobs(zuul, **kwargs)

    for job in jobs:
        # Check if the user requested variants
        if 'variants' in kwargs:
            for variant in perform_query_for_variants(job, **kwargs):
                model.with_variant(variant)

        # Check if the user requested builds
        if 'builds' in kwargs:
            for build in perform_query_for_builds(job, **kwargs):
                model.with_build(build)

        # Include also the pipelines where this job is present
        for pipeline in pipelines:
            if job.name in get_pipeline_jobs():
                model \
                    .with_pipeline(pipeline) \
                    .add_job(model.with_job(job))

        # In case nothing before has, register the job
        model.with_job(job)

    return model


def handle_query(zuul, **kwargs):
    """Generates and performs a query on a Zuul host based on the given
    arguments.

    :param zuul: API to interact with Zuul with.
    :type zuul: :class:`cibyl.sources.zuul.api.ZuulAPI`
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
    :key variants:
        Will fetch job variants too. Type: None.
    :key builds:
        Name of the builds to query. Type: AttributeListValue[str].
    :key builds_status:
        Status of the builds to query. Type: AttributeListValue[str].
    :key last_build:
        Will only return the newest build from the query. Type: None.
    :return: Resulting model generated from the query's response.
    :rtype: :class:`cibyl.sources.zuul.models.Model`
    """
    handlers = {
        QueryType.TENANTS: _handle_tenants_query,
        QueryType.PROJECTS: _handle_projects_query,
        QueryType.PIPELINES: _handle_pipelines_query,
        QueryType.JOBS: _handle_jobs_query,
        QueryType.BUILDS: _handle_jobs_query
    }

    query = get_query_type(**kwargs)
    handler = handlers.get(query)

    if not handler:
        raise NotImplementedError(f'Unsupported query: {query}')

    # Return generated model for the query
    return handler(zuul, **kwargs).assemble()
