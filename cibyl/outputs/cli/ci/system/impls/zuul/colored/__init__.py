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
import logging
from typing import Iterable

from overrides import overrides

import cibyl.outputs.cli.ci.system.common.features as features_query
from cibyl.cli.query import QueryType
from cibyl.models.ci.base.system import System
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.outputs.cli.ci.system.impls.base.colored import \
    ColoredBaseSystemPrinter
from cibyl.outputs.cli.ci.system.impls.zuul.colored.cascades.hierarchy import \
    HierarchyCascade
from cibyl.outputs.cli.ci.system.impls.zuul.colored.cascades.job import \
    JobCascade
from cibyl.outputs.cli.ci.system.impls.zuul.colored.cascades.project import \
    ProjectCascade
from cibyl.outputs.cli.ci.system.impls.zuul.colored.trees.factory import \
    HierarchicalTreeFactory
from kernel.tools.sorting import sort
from kernel.tools.text import IndentedTextBuilder

LOG = logging.getLogger(__name__)


class ColoredZuulSystemPrinter(ColoredBaseSystemPrinter):
    """Printer meant for :class:`ZuulSystem`, decorated with colors for
    easier read.
    """

    @overrides
    def print_system(self, system: System) -> str:
        printer = IndentedTextBuilder()

        # Begin with the text common to all systems
        printer.add(super().print_system(system), 0)

        if features_query.is_pure_features_query(self.query):
            # if the user has only requested features, there is no need to
            # print anything else
            return printer.build()
        # Continue with text specific for this system type
        if self.query >= QueryType.TENANTS:
            if hasattr(system, 'tenants'):
                if not system.is_queried():
                    msg = 'No query performed.'
                    printer.add(self.palette.blue(msg), 1)
                elif system.tenants.value:
                    for tenant in system.tenants.values():
                        printer.add(self.print_tenant(tenant), 1)

                    header = 'Total tenants found in query: '
                    printer.add(self.palette.blue(header), 1)
                    printer[-1].append(len(system.tenants))
                else:
                    msg = 'No tenants found in query.'
                    printer.add(self.palette.red(msg), 1)
            else:
                LOG.warning(
                    'Requested tenant printing on a non-zuul interface. '
                    'Ignoring...'
                )

        return printer.build()

    def print_tenant(self, tenant: Tenant) -> str:
        """
        :param tenant: The tenant.
        :return: Textual representation of the provided model.
        """
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Tenant: '), 0)
        result[-1].append(tenant.name)

        if self._is_projects_requested():
            result.add(self._print_projects_on(tenant), 1)

        if self._is_jobs_requested():
            result.add(self._print_jobs_on(tenant), 1)

        return result.build()

    def _is_projects_requested(self) -> bool:
        return any(
            option in self.query
            for option in (
                QueryType.PROJECTS,
                QueryType.PIPELINES
            )
        )

    def _is_jobs_requested(self) -> bool:
        return any(
            option in self.query
            for option in (
                QueryType.JOBS,
                QueryType.VARIANTS,
                QueryType.BUILDS,
                QueryType.TESTS
            )
        )

    def _print_projects_on(self, tenant: Tenant) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Projects: '), 0)

        if tenant.projects.value:
            for project in tenant.projects.values():
                printer = ProjectCascade(
                    self.query, self.verbosity, self.palette
                )

                result.add(printer.print_project(project), 1)

            result.add(
                self.palette.blue(
                    "Total projects found in query for tenant '"
                ), 0
            )
            result[-1].append(self.palette.underline(tenant.name))
            result[-1].append(self.palette.blue("': "))
            result[-1].append(len(tenant.projects))
        else:
            msg = 'No projects found in query.'
            result.add(self.palette.red(msg), 1)

        return result.build()

    def _print_jobs_on(self, tenant: Tenant) -> str:
        result = IndentedTextBuilder()

        result.add(self.palette.blue('Jobs: '), 0)

        if tenant.jobs.value:
            jobs = sort(tenant.jobs.values(), self._job_sorter)

            result.add(self._print_hierarchy_for(jobs), 1)
            result.add(self._print_list_for(jobs), 1)

            result.add(
                self.palette.blue(
                    "Total jobs found in query for tenant '"
                ), 0
            )

            result[-1].append(self.palette.underline(tenant.name))
            result[-1].append(self.palette.blue("': "))
            result[-1].append(len(tenant.jobs))
        else:
            msg = 'No jobs found in query.'
            result.add(self.palette.red(msg), 1)

        return result.build()

    def _print_hierarchy_for(self, jobs: Iterable[Job]) -> str:
        result = IndentedTextBuilder()

        trees = HierarchicalTreeFactory()
        printer = HierarchyCascade(self.query, self.verbosity, self.palette)

        tree = trees.from_jobs(jobs)

        result.add(self.palette.blue('Summary: '), 0)
        result.add(printer.print_tree(tree), 1)

        return result.build()

    def _print_list_for(self, jobs: Iterable[Job]) -> str:
        result = IndentedTextBuilder()

        printer = JobCascade(self.query, self.verbosity, self.palette)

        result.add(self.palette.blue('In detail: '), 0)

        for job in jobs:
            result.add(printer.print_job(job), 1)

        return result.build()
