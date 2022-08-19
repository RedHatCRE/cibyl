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
from unittest.mock import Mock, patch

from cibyl.sources.zuul.queries.composition.verbose import VerboseQuery

pkg = 'cibyl.sources.zuul.queries.composition'


class TestVerboseQuery(TestCase):
    """Tests for :class:`VerboseQuery`.
    """

    @patch(f'{pkg}.quick.perform_tenants_query')
    def test_gets_tenants(self, tenants: Mock):
        """Checks that the simple queries are made in order to aggregate
        tenants.
        """
        kwargs = {'arg1': 'val1'}

        tenant = Mock()

        api = Mock()
        builder = Mock()
        builder.with_tenant = Mock()

        tools = Mock()
        tools.builder = builder

        tenants.return_value = [tenant]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_tenants_query(**kwargs))

        tenants.assert_called_once_with(api, **kwargs)
        builder.with_tenant.assert_called_once_with(tenant)

    @patch(f'{pkg}.quick.perform_projects_query')
    def test_gets_projects(self, projects: Mock):
        """Checks that the simple queries are made in order to aggregate
        projects.
        """
        kwargs = {'arg1': 'val1'}

        tenant = Mock()

        api = Mock()
        builder = Mock()
        builder.with_project = Mock()

        tools = Mock()
        tools.builder = builder

        projects.return_value = [tenant]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_projects_query(**kwargs))

        projects.assert_called_once_with(api, **kwargs)
        builder.with_project.assert_called_once_with(tenant)

    @patch(f'{pkg}.quick.perform_pipelines_query')
    def test_gets_pipelines(self, pipelines: Mock):
        """Checks that the simple queries are made in order to aggregate
        pipelines.
        """
        kwargs = {'arg1': 'val1'}

        pipeline = Mock()

        api = Mock()
        builder = Mock()
        builder.with_pipeline = Mock()

        tools = Mock()
        tools.builder = builder

        pipelines.return_value = [pipeline]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_pipelines_query(**kwargs))

        pipelines.assert_called_once_with(api, **kwargs)
        builder.with_pipeline.assert_called_once_with(pipeline)

    @patch(f'{pkg}.verbose.perform_jobs_query')
    @patch(f'{pkg}.verbose.perform_pipelines_query')
    def test_gets_jobs(self, pipelines: Mock, jobs: Mock):
        """Checks that the simple queries are made in order to aggregate
        jobs.
        """
        kwargs = {'arg1': 'val1'}

        name = 'job'

        job = Mock()
        job.name = name

        pipeline = Mock()
        pipeline.jobs = Mock()
        pipeline.jobs.return_value = Mock()
        pipeline.jobs.return_value.get = Mock()
        pipeline.jobs.return_value.get.return_value = [job]

        pl_model = Mock()
        pl_model.add_job = Mock()
        job_model = Mock()

        api = Mock()
        builder = Mock()
        builder.with_pipeline = Mock()
        builder.with_pipeline.return_value = pl_model
        builder.with_job = Mock()
        builder.with_job.return_value = job_model

        tools = Mock()
        tools.builder = builder

        pipelines.return_value = [pipeline]
        jobs.return_value = [job]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_jobs_query(**kwargs))

        pipelines.assert_called_once_with(api, **kwargs)
        jobs.assert_called_once_with(api, **kwargs)

        builder.with_pipeline.assert_called_once_with(pipeline)
        builder.with_job.assert_called_once_with(job)

        pl_model.add_job.assert_called_once_with(job_model)

    @patch(f'{pkg}.quick.perform_variants_query')
    @patch(f'{pkg}.quick.perform_jobs_query')
    def test_gets_variants(self, jobs: Mock, variants: Mock):
        """Checks that the simple queries are made in order to aggregate
        variants.
        """
        kwargs = {'arg1': 'val1'}

        job = Mock()
        variant = Mock()

        api = Mock()
        builder = Mock()
        builder.with_variant = Mock()

        tools = Mock()
        tools.builder = builder

        jobs.return_value = [job]
        variants.return_value = [variant]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_variants_query(**kwargs))

        jobs.assert_called_once_with(api, **kwargs)
        variants.assert_called_once_with(job, **kwargs)

        builder.with_variant.assert_called_once_with(variant)

    @patch(f'{pkg}.quick.perform_builds_query')
    @patch(f'{pkg}.quick.perform_jobs_query')
    def test_gets_builds(self, jobs: Mock, builds: Mock):
        """Checks that the simple queries are made in order to aggregate
        builds.
        """
        kwargs = {'arg1': 'val1'}

        job = Mock()
        build = Mock()

        api = Mock()
        builder = Mock()
        builder.with_build = Mock()

        tools = Mock()
        tools.builder = builder

        jobs.return_value = [job]
        builds.return_value = [build]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_builds_query(**kwargs))

        jobs.assert_called_once_with(api, **kwargs)
        builds.assert_called_once_with(job, **kwargs)

        builder.with_build.assert_called_once_with(build)

    @patch(f'{pkg}.quick.perform_tests_query')
    @patch(f'{pkg}.quick.perform_builds_query')
    @patch(f'{pkg}.quick.perform_jobs_query')
    def test_gets_tests(self, jobs: Mock, builds: Mock, tests: Mock):
        """Checks that the simple queries are made in order to aggregate
        builds.
        """
        kwargs = {'arg1': 'val1'}

        job = Mock()
        build = Mock()
        test = Mock()

        api = Mock()
        builder = Mock()
        builder.with_test = Mock()

        tools = Mock()
        tools.builder = builder

        jobs.return_value = [job]
        builds.return_value = [build]
        tests.return_value = [test]

        query = VerboseQuery(api=api, tools=tools)

        self.assertEqual(query, query.with_tests_query(**kwargs))

        jobs.assert_called_once_with(api, **kwargs)
        builds.assert_called_once_with(job, **kwargs)
        tests.assert_called_once_with(build, **kwargs)

        builder.with_test.assert_called_once_with(test)
