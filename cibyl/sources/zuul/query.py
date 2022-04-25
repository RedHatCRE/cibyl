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


def _get_builds(zuul, **kwargs):
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
    result = []

    for tenant in _get_tenants(zuul, **kwargs):
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


def _get_tenants(zuul, **kwargs):
    tenants = TenantsRequest(zuul)

    # Apply tenants filters
    if 'tenants' in kwargs:
        targets = kwargs['tenants'].value

        # An empty '--tenants' means all of them.
        if targets:
            tenants.with_name(*targets)

    return tenants.get()


def handle_query(api, **kwargs):
    model = ModelBuilder()

    # Perform tenants query
    if 'tenants' in kwargs:
        for tenant in _get_tenants(api, **kwargs):
            model.with_tenant(tenant)

    # Perform jobs query
    if 'jobs' in kwargs:
        for job in _get_jobs(api, **kwargs):
            model.with_job(job)

    # Perform builds query
    if 'builds' in kwargs:
        for build in _get_builds(api, **kwargs):
            model.with_build(build)

    # Format the result
    return AttributeDictValue(
        name='tenants',
        attr_type=Tenant,
        value=model.assemble()
    )
