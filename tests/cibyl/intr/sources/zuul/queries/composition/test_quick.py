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

from cibyl.cli.argument import Argument
from cibyl.models.ci.zuul.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.models.ci.zuul.test import Test, TestKind, TestStatus
from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.sources.zuul.apis.factories.rest import ZuulRESTFactory
from cibyl.sources.zuul.arguments import ArgumentReview
from cibyl.sources.zuul.queries.composition.quick import QuickQuery
from cibyl.sources.zuul.source import Zuul
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest
from cibyl.sources.zuul.utils.tests.types import TestResult


class TestQuickQuery(TestCase):
    """Tests for :class:`QuickQuery`.
    """

    def test_tenants_query(self):
        """Checks that tenants are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        tenant.name = 'tenant'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'tenants': Argument('tenants', str, '')}
        result = source.get_tenants(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(name=tenant.name)
        }

        self.assertEqual(expected, models)

    def test_projects_query(self):
        """Checks that projects are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        project = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]

        project.name = 'project'
        project.url = 'http://localhost:8080/'
        project.tenant = tenant

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'projects': Argument('projects', str, '')}
        result = source.get_projects(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                projects={
                    project.name: Project(
                        name=project.name,
                        url=project.url
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_pipelines_query(self):
        """Checks that pipelines are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        project = Mock()
        pipeline = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]

        project.name = 'project'
        project.url = 'http://localhost:8080/'
        project.tenant = tenant
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline]

        pipeline.name = 'pipeline'
        pipeline.project = project

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'pipelines': Argument('pipelines', str, '')}
        result = source.get_pipelines(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                projects={
                    project.name: Project(
                        name=project.name,
                        url=project.url,
                        pipelines={
                            pipeline.name: Pipeline(
                                name=pipeline.name
                            )
                        }
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_jobs_query(self):
        """Checks that jobs are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        job = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant
        job.name = 'job'
        job.url = 'http://localhost:8080/'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'jobs': Argument('jobs', str, '')}
        result = source.get_jobs(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                jobs={
                    job.name: Job(
                        name=job.name,
                        url=job.url
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_variants_query(self):
        """Checks that variants are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        job = Mock()
        variant = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant
        job.name = 'job'
        job.url = 'http://localhost:8080/'
        job.variants = Mock()
        job.variants.return_value = [variant]

        variant.job = job
        variant.parent = None
        variant.name = 'variant'
        variant.description = 'desc'
        variant.branches = ['branch']
        variant.variables = {}

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {
            'jobs': Argument('jobs', str, ''),
            'variants': Argument('variants', str, '')
        }

        result = source.get_jobs(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                jobs={
                    job.name: Job(
                        name=job.name,
                        url=job.url,
                        variants=[
                            Job.Variant(
                                parent=variant.parent,
                                name=variant.name,
                                description=variant.description,
                                branches=variant.branches,
                                variables=variant.variables
                            )
                        ]
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_builds_query(self):
        """Checks that builds are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        job = Mock()
        build = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant
        job.name = 'job'
        job.url = 'http://localhost:8080/'
        job.builds = Mock()
        job.builds.return_value = [build]

        build.job = job
        build.raw = {
            'project': 'project',
            'pipeline': 'pipeline',
            'uuid': '1234',
            'result': 'success',
            'duration': 10
        }

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'builds': Argument('builds', str, '')}
        result = source.get_builds(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                jobs={
                    job.name: Job(
                        name=job.name,
                        url=job.url,
                        builds={
                            build.raw['uuid']: Build(
                                Build.Data(
                                    project=build.raw['project'],
                                    pipeline=build.raw['pipeline'],
                                    uuid=build.raw['uuid'],
                                    result=build.raw['result'],
                                    duration=build.raw['duration']
                                )
                            )
                        }
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_tests_query(self):
        """Checks that tests are retrieved from the host when the argument
        is found.
        """
        tenant = Mock()
        job = Mock()
        build = Mock()
        suite = Mock()
        test = Mock(spec=TempestTest)

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant
        job.name = 'job'
        job.url = 'http://localhost:8080/'
        job.builds = Mock()
        job.builds.return_value = [build]

        build.job = job
        build.raw = {
            'project': 'project',
            'pipeline': 'pipeline',
            'uuid': '1234',
            'result': 'success',
            'duration': 10
        }
        build.tests = Mock()
        build.tests.return_value = [suite]

        suite.name = 'suite'
        suite.url = 'http://localhost:8080/'
        suite.tests = [test]

        test.name = 'test'
        test.result = TestResult.SUCCESS
        test.duration = 10
        test.url = 'http://localhost:8080/'

        data = Mock()
        data.name = test.name
        data.status = TestStatus.SUCCESS
        data.duration = test.duration
        data.url = test.url

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {'tests': Argument('tests', str, '')}
        result = source.get_tests(**kwargs)

        models = result.value
        expected = {
            tenant.name: Tenant(
                name=tenant.name,
                jobs={
                    job.name: Job(
                        name=job.name,
                        url=job.url,
                        builds={
                            build.raw['uuid']: Build(
                                Build.Data(
                                    project=build.raw['project'],
                                    pipeline=build.raw['pipeline'],
                                    uuid=build.raw['uuid'],
                                    result=build.raw['result'],
                                    duration=build.raw['duration']
                                ),
                                suites=[
                                    TestSuite(
                                        TestSuite.Data(
                                            name=suite.name,
                                            url=suite.url,
                                            tests=[
                                                Test(
                                                    kind=TestKind.TEMPEST,
                                                    data=data
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        }
                    )
                }
            )
        }

        self.assertEqual(expected, models)

    def test_mixed_tenants_projects(self):
        """Checks that the combined answer of tenants and projects can be
        returned.
        """
        tenant1 = Mock()
        tenant2 = Mock()

        project = Mock()

        tenant1.name = 'tenant1'
        tenant1.projects = Mock()
        tenant1.projects.return_value = [project]

        tenant2.name = 'tenant2'
        tenant2.projects = Mock()
        tenant2.projects.return_value = []

        project.name = 'project'
        project.tenant = tenant1

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant1, tenant2]

        query = QuickQuery(api)

        factory = Mock()
        factory.from_kwargs = Mock()
        factory.from_kwargs.return_value = query

        tools = Zuul.Tools(
            api=ZuulRESTFactory(),
            arguments=ArgumentReview(),
            query=factory
        )

        source = Zuul(
            name='test-source',
            driver='zuul',
            url='http://localhost:8080/',
            tools=tools
        )

        kwargs = {
            'tenants': Argument('tenants', str, ''),
            'projects': Argument('projects', str, '')
        }
        result = source.get_projects(**kwargs)

        models = result.value
        expected = {
            tenant1.name: Tenant(
                name=tenant1.name,
                projects={
                    project.name: Project(
                        name=project.name,
                        url=project.url
                    )
                }
            ),
            tenant2.name: Tenant(
                name=tenant2.name
            )
        }

        self.assertEqual(expected, models)
