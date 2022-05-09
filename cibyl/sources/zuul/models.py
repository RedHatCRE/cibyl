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
from cibyl.models.ci.project import Project
from cibyl.models.ci.tenant import Tenant


class ModelBuilder:
    """Utility used to generate CI models out of data retrieved from the
    Zuul host.
    """

    def __init__(self):
        """Constructor.
        """
        self._tenants = {}

    def with_tenant(self, tenant):
        """Adds a tenant to the current model being built. If the tenant is
        already present on the model, then this is ignored.

        :param tenant: The tenant to add.
        :type tenant: :class:`cibyl.sources.zuul.requests.TenantResponse`
        :return: The builder's instance.
        :rtype: :class:`ModelBuilder`
        """
        if not self._get_tenant(tenant.name):
            self._tenants[tenant.name] = Tenant(tenant.name)

        return self

    def with_project(self, project):
        """Adds a project to the current model being built. If the project is
        already present on the model, then this is ignored. If the project's
        tenant is not on the model, then it is also added to it.

        :param project: The project to add.
        :type project: :class:`cibyl.sources.zuul.requests.ProjectResponse`
        :return: The builder's instance.
        :rtype: :class:`ModelBuilder`
        """
        model = Project(project.name, project.url)

        # Register the project's tenant
        self.with_tenant(project.tenant)

        # Register the project
        tenant = self._get_tenant(project.tenant.name)
        tenant.add_project(model)

        return self

    def with_job(self, job):
        """Adds a job to the current model being built. If the job is
        already present on the model, then this is ignored. If the job's
        tenant is not on the model, then it is also added to it.

        :param job: The job to add.
        :type job: :class:`cibyl.sources.zuul.requests.JobResponse`
        :return: The builder's instance.
        :rtype: :class:`ModelBuilder`
        """
        model = Job(job.name, job.url)

        # Register the job's tenant
        self.with_tenant(job.tenant)

        # Register the job
        tenant = self._get_tenant(job.tenant.name)
        tenant.add_job(model)

        return self

    def with_build(self, build):
        """Adds a build to the current model being built. If the build is
        already present on the model, then this is ignored. If the build's
        job is not on the model, then it is also added to it.

        :param build: The build to add.
        :type build: :class:`cibyl.sources.zuul.requests.BuildResponse`
        :return: The builder's instance.
        :rtype: :class:`ModelBuilder`
        """
        model = Build(
            build.data['uuid'],
            build.data['result'],
            build.data['duration']
        )

        # Register the build's job
        self.with_job(build.job)

        # Register the build
        job = self._get_job(build.job.name)
        job.add_build(model)

        return self

    def assemble(self):
        """Generates the CI model.

        :return: The model.
        :rtype: dict[str, :class:`Tenant`]
        """
        return self._tenants

    def _get_tenant(self, name):
        """Searches the model for a certain tenant.

        :param name: Name of the tenant.
        :type name: str
        :return: The tenant's model.
        :rtype: :class:`Tenant` or None
        """
        return self._tenants.get(name)

    def _get_job(self, name):
        """Searches the model for a certain job.

        :param name: Name of the job.
        :type name: str
        :return: The job's model.
        :rtype: :class:`Job` or None
        """
        for tenant in self._tenants.values():
            if name in tenant.jobs.value:
                return tenant.jobs.value[name]
