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
from unittest.mock import Mock

from cibyl.cli.query import QueryType
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.system import JobsSystem
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.outputs.cli.ci.system.impls.jobs import colored
from cibyl.outputs.cli.ci.system.impls.zuul import colored as zuul_colored
from tests.cibyl.utils import (OpenstackPluginWithJobSystem,
                               OpenstackPluginWithZuulSystem)


class TestOutputJobsSystemWithOpenstackPlugin(OpenstackPluginWithJobSystem):
    """Test publisher output with openstack plugin."""

    def test_empty_openstack_attributes(self):
        system = JobsSystem("test-system", "test")
        for i in range(3):
            job_name = f"job-name-{i}"
            system.add_job(Job(name=job_name))
        system.register_query()

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = lambda text: text

        printer = colored.ColoredJobsSystemPrinter(palette=palette,
                                                   query=QueryType.JOBS)
        output = printer.print_system(system)
        # check that output is five lines long(system line, one line per job
        # and the line for total number of jobs)
        self.assertEqual(5, len(output.split("\n")))
        expected = "System: test-system"
        for i in range(3):
            expected += f"\n  Job: job-name-{i}"
        expected += "\n  Total jobs found in query: 3"
        self.assertEqual(output, expected)


class TestOutputZuulSystemWithOpenstackPlugin(OpenstackPluginWithZuulSystem):
    """Test publisher output with openstack plugin."""

    def test_empty_openstack_attributes(self):
        system = ZuulSystem("test-system", "test")
        jobs = {}
        for i in range(3):
            job_name = f"job-name-{i}"
            jobs[job_name] = Job(name=job_name)
        pipeline = Pipeline(name="pipeline", jobs=jobs)
        project = Project("project", url="url",
                          pipelines={'pipeline': pipeline})
        tenant = Tenant("tenant", projects={'project': project})
        system.add_toplevel_model(tenant)
        system.register_query()

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = lambda text: text
        palette.red = Mock()
        palette.red.side_effect = lambda text: text
        palette.underline = Mock()
        palette.underline.side_effect = lambda text: text

        printer = zuul_colored.ColoredZuulSystemPrinter(
            palette=palette,
            query=QueryType.PIPELINES | QueryType.JOBS
        )
        output = printer.print_system(system)
        # check that output is five lines long(system line, one line per job
        # and the line for total number of jobs)
        self.assertEqual(14, len(output.split("\n")))

        expected = "System: test-system\n"
        expected += "  Tenant: tenant\n"
        expected += "    Projects: \n"
        expected += "      Project: project\n"
        expected += "        Pipeline: pipeline"
        for i in range(3):
            expected += f"\n          Job: job-name-{i}"
        expected += "\n          Total jobs found in query for pipeline"
        expected += " 'pipeline': 3\n"
        expected += "        Total pipelines found in query for project"
        expected += " 'project': 1\n"
        expected += "    Total projects found in query for tenant"
        expected += " 'tenant': 1\n"
        expected += "    Jobs: \n"
        expected += "      No jobs found in query.\n"
        expected += "  Total tenants found in query: 1"
        self.assertEqual(output, expected)
