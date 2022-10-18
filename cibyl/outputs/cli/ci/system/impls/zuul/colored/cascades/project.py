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
import cibyl.outputs.cli.ci.system.common.features as features_query
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.outputs.cli.ci.system.common.builds import get_status_section
from cibyl.outputs.cli.printer import ColoredPrinter
from cibyl.utils.filtering import apply_filters
from cibyl.utils.strings import IndentedTextBuilder


class ProjectCascade(ColoredPrinter):
    """Printer meant for :class:`Project` and all of its children. This
    printer focuses more on providing a high-level view of the
    relationship between elements more than their details.
    """

    def print_project(self, project: Project) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Project: '), 0)
        result[-1].append(project.name)

        if self.verbosity > 0:
            result.add(self.palette.blue('URL: '), 1)
            result[-1].append(project.url)

        if self.query >= QueryType.PIPELINES:
            if project.pipelines.value:
                for pipeline in project.pipelines.values():
                    result.add(self.print_pipeline(project, pipeline), 1)

                msg = "Total pipelines found in query for project '"
                result.add(self.palette.blue(msg), 1)
                result[-1].append(self.palette.underline(project.name))
                result[-1].append(self.palette.blue("': "))
                result[-1].append(len(project.pipelines))
            else:
                msg = 'No pipelines found in query.'
                result.add(self.palette.red(msg), 1)

        return result.build()

    def print_pipeline(self, project: Project, pipeline: Pipeline) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Pipeline: '), 0)
        result[-1].append(pipeline.name)

        if self.query >= QueryType.JOBS:
            if pipeline.jobs.value:
                for job in pipeline.jobs.values():
                    result.add(self.print_job(project, pipeline, job), 1)

                msg = "Total jobs found in query for pipeline '"
                result.add(self.palette.blue(msg), 1)
                result[-1].append(self.palette.underline(pipeline.name))
                result[-1].append(self.palette.blue("': "))
                result[-1].append(len(pipeline.jobs))
            else:
                msg = 'No jobs found in query.'
                result.add(self.palette.red(msg), 1)

        return result.build()

    def print_job(self, project: Project, pipeline: Pipeline,
                  job: Job) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Job: '), 0)
        result[-1].append(job.name.value)

        if features_query.is_features_query(self.query):
            # if features are used, do not print further below
            return result.build()

        if self.query >= QueryType.BUILDS:
            builds = apply_filters(
                job.builds.values(),
                lambda bld: bld.project.value == project.name.value,
                lambda bld: bld.pipeline.value == pipeline.name.value
            )

            if builds:
                for build in builds:
                    msg = self.print_build(project, pipeline, job, build)
                    result.add(msg, 1)
            else:
                msg = 'No builds in query.'
                result.add(self.palette.red(msg), 1)

        return result.build()

    def print_build(self, project: Project, pipeline: Pipeline, job: Job,
                    build: Build) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Build: '), 1)
        result[-1].append(build.build_id.value)

        if build.status.value:
            result.add(get_status_section(self.palette, build), 2)

        return result.build()
