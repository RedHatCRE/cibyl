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
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.zuul.apis.factories.rest import ZuulRESTFactory
from cibyl.sources.zuul.arguments import ArgumentReview
from cibyl.sources.zuul.queries.composition.verbose import VerboseQuery
from cibyl.sources.zuul.source import Zuul


class TestVerboseQuery(TestCase):
    """Tests for :class:`VerboseQuery`.
    """

    def test_jobs_fetches_pipelines(self):
        """Checks that looking for jobs will also get you the pipelines
        they belong to.
        """
        tenant = Mock()
        project = Mock()
        pipeline = Mock()
        job = Mock()

        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        project.name = 'project'
        project.url = 'http://localhost:8080/'
        project.tenant = tenant
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline]

        pipeline.name = 'pipeline'
        pipeline.project = project
        pipeline.jobs = Mock()
        pipeline.jobs.return_value = [job]

        job.tenant = tenant
        job.name = 'job'
        job.url = 'http://localhost:8080/'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        query = VerboseQuery(api)

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
                projects={
                    project.name: Project(
                        name=project.name,
                        url=project.url,
                        pipelines={
                            pipeline.name: Pipeline(
                                name=pipeline.name,
                                jobs={
                                    job.name: Job(
                                        name=job.name,
                                        url=job.url
                                    )
                                }
                            )
                        }
                    )
                },
                jobs={
                    job.name: Job(
                        name=job.name,
                        url=job.url
                    )
                }
            )
        }

        self.assertEqual(expected, models)
