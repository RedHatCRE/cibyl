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
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.models.ci.tenant import Tenant


class ModelBuilder:
    def __init__(self):
        self._tenants = {}

    def with_tenant(self, tenant):
        if not self._get_tenant(tenant.name):
            self._tenants[tenant.name] = Tenant(tenant.name)

        return self

    def with_job(self, job):
        model = Job(job.name, job.url)

        tenant = self._get_tenant(job.tenant.name)

        if not tenant:
            self.with_tenant(job.tenant)
            tenant = self._get_tenant(job.tenant.name)

        tenant.add_job(model)
        return self

    def with_build(self, build):
        model = Build(
            build.data['uuid'],
            build.data['result'],
            build.data['duration']
        )

        job = self._get_job(build.job.name)

        if not job:
            self.with_job(build.job)
            job = self._get_job(build.job.name)

        job.add_build(model)
        return self

    def assemble(self):
        return self._tenants

    def _get_tenant(self, name):
        return self._tenants.get(name)

    def _get_job(self, name):
        for tenant in self._tenants.values():
            if name in tenant.jobs.value:
                return tenant.jobs.value[name]

        return None
