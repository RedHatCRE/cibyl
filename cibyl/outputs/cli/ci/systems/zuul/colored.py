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

from cibyl.cli.query import QueryType
from cibyl.outputs.cli.ci.systems.base.colored import ColoredBaseSystemPrinter
from cibyl.outputs.cli.ci.systems.common.jobs import get_plugin_section
from cibyl.utils.strings import IndentedTextBuilder


class ColoredZuulSystemPrinter(ColoredBaseSystemPrinter):
    @overrides
    def print_system(self, system):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('System: '), 0)
        printer[-1].append(system.name.value)

        if self.verbosity > 0:
            printer[-1].append(f' (type: {system.system_type.value})')

        if self.query != QueryType.NONE:
            for tenant in system.tenants.values():
                printer.add(self.print_tenant(tenant), 1)

            if system.is_queried():
                header = 'Total tenants found in query: '

                printer.add(self._palette.blue(header), 1)
                printer[-1].append(len(system.tenants))
            else:
                printer.add(self._palette.blue('No query performed'), 1)

        return printer.build()

    def print_tenant(self, tenant):
        def print_projects():
            result.add(self._palette.blue('Projects: '), 1)

            for project in tenant.projects.values():
                result.add(self.print_project(project), 2)

            result.add(
                self._palette.blue("Total projects found in tenant '"), 1
            )

            result[-1].append(self._palette.underline(tenant.name))
            result[-1].append(self._palette.blue("': "))
            result[-1].append(len(tenant.projects))

        def print_jobs():
            result.add(self._palette.blue('Jobs: '), 1)

            for job in tenant.jobs.values():
                result.add(self.print_job(job), 2)

            result.add(
                self._palette.blue("Total jobs found in tenant '"), 1
            )

            result[-1].append(self._palette.underline(tenant.name))
            result[-1].append(self._palette.blue("': "))
            result[-1].append(len(tenant.jobs))

        result = IndentedTextBuilder()

        result.add(self._palette.blue('Tenant: '), 0)
        result[-1].append(tenant.name)

        if self.query >= QueryType.JOBS:
            print_jobs()

        if self.query >= QueryType.PROJECTS:
            print_projects()

        return result.build()

    def print_project(self, project):
        result = IndentedTextBuilder()

        result.add(self._palette.blue('Project: '), 0)
        result[-1].append(project.name)

        if self.verbosity > 0:
            result.add(self._palette.blue('URL: '), 1)
            result[-1].append(project.url)

        if self.query > QueryType.PROJECTS:
            for pipeline in project.pipelines.values():
                result.add(self.print_pipeline(pipeline), 1)

            result.add(
                self._palette.blue("Total pipelines found in project '"), 1
            )

            result[-1].append(self._palette.underline(project.name))
            result[-1].append(self._palette.blue("': "))
            result[-1].append(len(project.pipelines))

        return result.build()

    def print_pipeline(self, pipeline):
        result = IndentedTextBuilder()

        result.add(self._palette.blue('Pipeline: '), 0)
        result[-1].append(pipeline.name)

        if self.query > QueryType.PIPELINES:
            for job in pipeline.jobs.values():
                result.add(self.print_job(job), 1)

            result.add(
                self._palette.blue('Total jobs found in pipeline '), 1
            )

            result[-1].append(self._palette.underline(pipeline.name))
            result[-1].append(self._palette.blue(': '))
            result[-1].append(len(pipeline.jobs))

        return result.build()

    @overrides
    def print_job(self, job):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Job: '), 0)
        printer[-1].append(job.name.value)

        if self.verbosity > 0:
            if job.url.value:
                printer.add(self._palette.blue('URL: '), 1)
                printer[-1].append(job.url.value)

        if job.variants.value:
            printer.add(self._palette.blue('Variants: '), 1)

            for variant in job.variants:
                printer.add(self.print_variant(variant), 2)

        if job.builds.value:
            printer.add(self._palette.blue('Builds: '), 1)

            for build in job.builds.values():
                printer.add(self.print_build(build), 2)

        printer.add(get_plugin_section(self, job), 1)

        return printer.build()

    def print_variant(self, variant):
        printer = IndentedTextBuilder()

        printer.add(self._palette.blue('Variant: '), 0)

        printer.add(self._palette.blue('Description: '), 1)
        printer[-1].append(variant.description)

        printer.add(self._palette.blue('Parent: '), 1)
        printer[-1].append(variant.parent)

        printer.add(self._palette.blue('Branches: '), 1)
        for branch in variant.branches:
            printer.add('- ', 2)
            printer[-1].append(branch)

        printer.add(self._palette.blue('Variables: '), 1)
        for key, value in variant.variables.items():
            printer.add(self._palette.blue(f'{key}: '), 2)
            printer[-1].append(value)

        return printer.build()
