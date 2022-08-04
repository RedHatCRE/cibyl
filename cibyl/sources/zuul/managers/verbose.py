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
from overrides import overrides

from cibyl.sources.zuul.managers import SourceManager
from cibyl.sources.zuul.output import QueryOutput
from cibyl.sources.zuul.queries.builds import perform_builds_query
from cibyl.sources.zuul.queries.jobs import perform_jobs_query
from cibyl.sources.zuul.queries.pipelines import perform_pipelines_query
from cibyl.sources.zuul.queries.projects import perform_projects_query
from cibyl.sources.zuul.queries.tenants import perform_tenants_query
from cibyl.sources.zuul.queries.variants import perform_variants_query


class VerboseManager(SourceManager):
    """Performs the source's queries retrieving as much information as it
    can from them.
    """

    @overrides
    def handle_tenants_query(self, **kwargs) -> QueryOutput:
        model = self.tools.output.new()

        for tenant in perform_tenants_query(self.api, **kwargs):
            model.with_tenant(tenant)

        return model.assemble()

    @overrides
    def handle_projects_query(self, **kwargs) -> QueryOutput:
        model = self.tools.output.new()

        if 'tenants' in kwargs:
            for tenant in perform_tenants_query(self.api, **kwargs):
                model.with_tenant(tenant)

        for project in perform_projects_query(self.api, **kwargs):
            model.with_project(project)

        return model.assemble()

    @overrides
    def handle_pipelines_query(self, **kwargs) -> QueryOutput:
        model = self.tools.output.new()

        if 'tenants' in kwargs:
            for tenant in perform_tenants_query(self.api, **kwargs):
                model.with_tenant(tenant)

        if 'projects' in kwargs:
            for project in perform_projects_query(self.api, **kwargs):
                model.with_project(project)

        for pipeline in perform_pipelines_query(self.api, **kwargs):
            model.with_pipeline(pipeline)

        return model.assemble()

    @overrides
    def handle_jobs_query(self, **kwargs) -> QueryOutput:
        def get_pipeline_jobs():
            return [j.name for j in pipeline.jobs().get()]

        model = self.tools.output.new()

        if 'tenants' in kwargs:
            for tenant in perform_tenants_query(self.api, **kwargs):
                model.with_tenant(tenant)

        if 'projects' in kwargs:
            for project in perform_projects_query(self.api, **kwargs):
                model.with_project(project)

        pipelines = perform_pipelines_query(self.api, **kwargs)

        if 'pipelines' in kwargs:
            for pipeline in pipelines:
                model.with_pipeline(pipeline)

        jobs = perform_jobs_query(self.api, **kwargs)

        for job in jobs:
            # Check if the user requested variants
            if 'variants' in kwargs:
                for variant in perform_variants_query(job, **kwargs):
                    model.with_variant(variant)

            # Check if the user requested builds
            if 'builds' in kwargs:
                for build in perform_builds_query(job, **kwargs):
                    model.with_build(build)

            # Include also the pipelines where this job is present
            for pipeline in pipelines:
                if job.name in get_pipeline_jobs():
                    model \
                        .with_pipeline(pipeline) \
                        .add_job(model.with_job(job))

            # In case nothing before has, register the job
            model.with_job(job)

        return model.assemble()

    @overrides
    def handle_variants_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @overrides
    def handle_builds_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError

    @overrides
    def handle_tests_query(self, **kwargs) -> QueryOutput:
        raise NotImplementedError
