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
from cibyl.models.ci.zuul.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant


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
        :return: Model for this tenant.
        :rtype: :class:`Tenant`
        """
        model = self._tenants.get(
            tenant.name,
            Tenant(tenant.name)
        )

        # Register the tenant
        if tenant.name not in self._tenants:
            self._tenants[tenant.name] = model

        return model

    def with_project(self, project):
        """Adds a project to the current model being built. If the project is
        already present on the model, then this is ignored. If the project's
        tenant is not on the model, then it is also added to it.

        :param project: The project to add.
        :type project: :class:`cibyl.sources.zuul.requests.ProjectResponse`
        :return: Model for this project.
        :rtype: :class:`Project`
        """
        # Register this project's tenant
        tenant = self.with_tenant(project.tenant)

        # Check if the project already exists
        model = tenant.projects.get(
            project.name,
            Project(project.name, project.url)
        )

        # Register this project
        tenant.add_project(model)

        return model

    def with_pipeline(self, pipeline):
        """Adds a pipeline to the current model being built. If the pipeline is
        already present on the model, then this is ignored. If the pipeline's
        tenant is not on the model, then it is also added to it.

        :param pipeline: The pipeline to add.
        :type pipeline: :class:`cibyl.sources.zuul.requests.PipelineResponse`
        :return: Model for this pipeline.
        :rtype: :class:`Pipeline`
        """
        # Register this pipeline's project
        project = self.with_project(pipeline.project)

        # Check if the pipeline already exists
        model = project.pipelines.get(
            pipeline.name,
            Pipeline(pipeline.name)
        )

        # Register the pipeline
        project.add_pipeline(model)

        return model

    def with_job(self, job):
        """Adds a job to the current model being built. If the job is
        already present on the model, then this is ignored. If the job's
        tenant is not on the model, then it is also added to it.

        :param job: The job to add.
        :type job: :class:`cibyl.sources.zuul.requests.JobResponse`
        :return: Model for this job.
        :rtype: :class:`Job`
        """
        # Register this job's tenant
        tenant = self.with_tenant(job.tenant)

        # Check if the job already exists
        model = tenant.jobs.get(
            job.name,
            Job(job.name, job.url)
        )

        # Register the job
        tenant.add_job(model)

        return model

    def with_variant(self, variant):
        """Adds a job variant to the current model being built. The variant
        will always be added, as there is no index to identify if it is already
        present on the model. So, watch out for duplicates. If the variant's
        job is not on the model, then it is also added.

        :param variant: The variant to add.
        :type variant: :class:`cibyl.sources.zuul.requests.VariantResponse`
        :return: Model for this variant
        :rtype: :class:`Job.Variant`
        """
        # Register this variant's job
        job = self.with_job(variant.job)

        # Generate the variant's model
        model = Job.Variant.from_data(variant.data)

        # Register the variant
        job.add_variant(model)

        return model

    def with_build(self, build):
        """Adds a build to the current model being built. If the build is
        already present on the model, then this is ignored. If the build's
        job is not on the model, then it is also added to it.

        :param build: The build to add.
        :type build: :class:`cibyl.sources.zuul.requests.BuildResponse`
        :return: Model for this build.
        :rtype: :class:`Build`
        """
        # Register this build's job
        job = self.with_job(build.job)

        # Check if the build already exists
        model = job.builds.get(
            build.data['uuid'],
            Build(
                Build.Info(
                    project=build.data['project'],
                    pipeline=build.data['pipeline'],
                    uuid=build.data['uuid'],
                    result=build.data['result'],
                    duration=build.data['duration']
                )
            )
        )

        # Register the build
        job.add_build(model)

        return model

    def assemble(self):
        """Generates the CI model.

        :return: The model.
        :rtype: dict[str, :class:`Tenant`]
        """
        return self._tenants
