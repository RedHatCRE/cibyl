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
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.tenant import Tenant
from cibyl.sources.zuul.models import ModelBuilder
from cibyl.sources.zuul.requests import TenantsRequest


def _is_keyword_on_args(*keyword, **kwargs):
    return any(key in kwargs for key in keyword)


def _asked_for_builds(**kwargs):
    return _is_keyword_on_args('builds', **kwargs)


def _asked_for_jobs(**kwargs):
    if _asked_for_builds(**kwargs):
        return True

    return _is_keyword_on_args('jobs', **kwargs)


def _asked_for_tenants(**kwargs):
    if _asked_for_jobs(**kwargs):
        return True

    return _is_keyword_on_args('tenants', **kwargs)


def _handle_builds(job, builder, **kwargs):
    if not _asked_for_builds(**kwargs):
        return

    builds = job.builds()

    # Apply builds filters
    if 'builds' in kwargs:
        builds.with_uuid(*kwargs['builds'].value)

    if 'build_status' in kwargs:
        statuses = kwargs['build_status'].value
        builds.with_status(*statuses)

    if 'last_build' in kwargs:
        builds.with_last_build_only()

    for build in builds.get():
        builder.with_build(build)


def _handle_jobs(tenant, builder, **kwargs):
    if not _asked_for_jobs(**kwargs):
        return

    jobs = tenant.jobs()

    # Apply jobs filters
    if 'jobs' in kwargs:
        targets = kwargs['jobs'].value

        # An empty '--jobs' means all jobs.
        if targets:
            jobs.with_name(*targets)

    if 'job_url' in kwargs:
        jobs.with_url(*kwargs['job_url'].value)

    for job in jobs.get():
        builder.with_job(job)
        _handle_builds(job, builder, **kwargs)


def _handle_tenants(zuul, builder, **kwargs):
    if not _asked_for_tenants(**kwargs):
        return

    tenants = TenantsRequest(zuul)

    # Apply tenants filters

    for tenant in tenants.get():
        builder.with_tenant(tenant)
        _handle_jobs(tenant, builder, **kwargs)


def handle_query(api, **kwargs):
    model = ModelBuilder()

    # Perform the query
    _handle_tenants(api, model, **kwargs)

    # Format the result
    return AttributeDictValue(
        name='tenants',
        attr_type=Tenant,
        value=model.assemble()
    )
