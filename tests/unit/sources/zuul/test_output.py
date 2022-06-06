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
from unittest import TestCase
from unittest.mock import Mock

from cibyl.sources.zuul.output import QueryOutputBuilder


class TestQueryOutputBuilder(TestCase):
    """Tests for :class:`QueryOutputBuilder`.
    """

    def assertNotRaises(self, action, error):
        try:
            action()
        except error:
            self.fail(f'Raised undesired error of type: {error}')

    def test_with_unknown_tenant(self):
        """Checks that a tenant is generated if it is unknown.
        """
        tenant = Mock()
        tenant.name = 'name'

        builder = QueryOutputBuilder()
        builder.with_tenant(tenant)

        result = builder.assemble()

        self.assertIn(tenant.name, result.keys())
        self.assertEqual(tenant.name, result[tenant.name].name.value)

    def test_with_known_tenant(self):
        """Checks that no error happens if a tenant is added twice.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        builder = QueryOutputBuilder()
        builder.with_tenant(tenant)

        self.assertNotRaises(lambda: builder.with_tenant(tenant), Exception)

    def test_with_project_of_unknown_tenant(self):
        """Checks that a new tenant is generated if a project belonging to
        an unknown one is added.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        project = Mock()
        project.tenant = tenant

        builder = QueryOutputBuilder()
        builder.with_project(project)

        result = builder.assemble()

        self.assertIn(project.tenant.name, result.keys())

        result_tenant = result[tenant.name]
        result_project = result_tenant.projects[project.name]

        self.assertEqual(tenant.name, result_tenant.name.value)
        self.assertEqual(project.name, result_project.name.value)

    def test_with_pipeline_of_unknown_project(self):
        """Checks that a new project and tenant is generated if a pipeline
        belonging to unknown ones is added.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        project = Mock()
        project.tenant = tenant

        pipeline = Mock()
        pipeline.project = project

        builder = QueryOutputBuilder()
        builder.with_pipeline(pipeline)

        result = builder.assemble()

        self.assertIn(tenant.name, result.keys())

        result_tenant = result[tenant.name]
        result_project = result_tenant.projects[project.name]
        result_pipeline = result_project.pipelines[pipeline.name]

        self.assertEqual(tenant.name, result_tenant.name.value)
        self.assertEqual(project.name, result_project.name.value)
        self.assertEqual(pipeline.name, result_pipeline.name.value)

    def test_with_job_of_unknown_tenant(self):
        """Checks that a new tenant is generated if a job belonging to an
        unknown one is added.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        job = Mock()
        job.tenant = tenant
        job.name = 'job'
        job.url = 'url'

        builder = QueryOutputBuilder()
        builder.with_job(job)

        result = builder.assemble()

        self.assertIn(job.tenant.name, result.keys())

        result_tenant = result[tenant.name]
        result_job = result_tenant.jobs[job.name]

        self.assertEqual(tenant.name, result_tenant.name.value)
        self.assertEqual(job.name, result_job.name.value)

    def test_with_build_of_unknown_job(self):
        """Checks that a new job is generated if a build belonging to an
        unknown one is added.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        job = Mock()
        job.tenant = tenant
        job.name = 'job'
        job.url = 'url'

        build = Mock()
        build.job = job
        build.data = {
            'uuid': 'id',
            'result': 'SUCCESS',
            'project': 'project',
            'pipeline': 'pipeline',
            'duration': 0
        }

        builder = QueryOutputBuilder()
        builder.with_build(build)

        result = builder.assemble()

        self.assertIn(job.tenant.name, result.keys())

        result_tenant = result[tenant.name]
        result_job = result_tenant.jobs[job.name]
        result_build = result_job.builds[build.data['uuid']]

        self.assertEqual(tenant.name, result_tenant.name.value)
        self.assertEqual(job.name, result_job.name.value)

        self.assertEqual(build.data['uuid'], result_build.build_id.value)
        self.assertEqual(build.data['result'], result_build.status.value)
        self.assertEqual(build.data['duration'], result_build.duration.value)
