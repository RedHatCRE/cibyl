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

from cibyl.models.ci.build import Build
from cibyl.models.ci.zuul.job import Job
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.zuul.query import handle_query


class DictMock(Mock):
    """A mock that acts as a dictionary.
    """

    def __init__(self):
        super().__init__()

        self._data = {}

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value


class TestHandleQuery(TestCase):
    """Tests the correct retrieval and processing of data from a Zuul
    source.

    This is an integration test that combines the :mod:`query`, :mod:`cli`,
    :mod:`models` and :mod:`requests` modules.
    """

    def test_get_all_tenants(self):
        """Checks the '--tenant' option.
        """
        tenant1 = Mock()
        tenant1.name = 'tenant1'

        tenant2 = Mock()
        tenant2.name = 'tenant2'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant1, tenant2]

        in_tenants = Mock()
        in_tenants.value = None

        result = handle_query(api, tenants=in_tenants)

        self.assertEqual(
            {
                tenant1.name: Tenant(tenant1.name),
                tenant2.name: Tenant(tenant2.name)
            },
            result.value
        )

    def test_get_tenants_by_name(self):
        """Checks the '--tenant pattern1 pattern2' option.
        """
        tenant1 = Mock()
        tenant1.name = 'tenant1'

        tenant2 = Mock()
        tenant2.name = 'tenant2'

        tenant3 = Mock()
        tenant3.name = 'tenant3'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant1, tenant2, tenant3]

        in_tenants = Mock()
        in_tenants.value = [f'({tenant1.name})']

        result = handle_query(api, tenants=in_tenants)

        self.assertEqual(
            {
                tenant1.name: Tenant(tenant1.name)
            },
            result.value
        )

    def test_get_all_projects(self):
        """Checks the '--projects' option.
        """
        project1 = Mock()
        project1.name = 'project1'
        project1.url = 'url1'

        project2 = Mock()
        project2.name = 'project2'
        project2.url = 'url2'

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project1, project2]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        project1.tenant = tenant
        project2.tenant = tenant

        in_projects = Mock()
        in_projects.value = None

        result = handle_query(api, projects=in_projects)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project1.name: Project(project1.name, project1.url),
                        project2.name: Project(project2.name, project2.url)
                    }
                )
            },
            result.value
        )

    def test_get_projects_by_name(self):
        """Checks the '--projects pattern1 pattern2' option.
        """
        project1 = Mock()
        project1.name = 'project1'
        project1.url = 'url1'

        project2 = Mock()
        project2.name = 'project2'
        project2.url = 'url2'

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project1, project2]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        project1.tenant = tenant
        project2.tenant = tenant

        in_projects = Mock()
        in_projects.value = [f'({project1.name})']

        result = handle_query(api, projects=in_projects)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project1.name: Project(project1.name, project1.url)
                    }
                )
            },
            result.value
        )

    def test_get_all_pipelines(self):
        """Checks the '--pipelines' option.
        """
        pipeline1 = Mock()
        pipeline1.name = 'pipeline1'

        pipeline2 = Mock()
        pipeline2.name = 'pipeline2'

        project = Mock()
        project.name = 'project'
        project.url = 'url'
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline1, pipeline2]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        pipeline1.project = project
        pipeline2.project = project

        project.tenant = tenant

        in_pipelines = Mock()
        in_pipelines.value = None

        result = handle_query(api, pipelines=in_pipelines)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project.name: Project(
                            project.name,
                            project.url,
                            pipelines={
                                pipeline1.name: Pipeline(pipeline1.name),
                                pipeline2.name: Pipeline(pipeline2.name)
                            }
                        )
                    }
                )
            },
            result.value
        )

    def test_get_pipelines_by_name(self):
        """Checks the '--pipelines pattern1 pattern2' option.
        """
        pipeline1 = Mock()
        pipeline1.name = 'pipeline1'

        pipeline2 = Mock()
        pipeline2.name = 'pipeline2'

        pipeline3 = Mock()
        pipeline3.name = 'pipeline3'

        project = Mock()
        project.name = 'project'
        project.url = 'url'
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline1, pipeline2, pipeline3]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        pipeline1.project = project
        pipeline2.project = project

        project.tenant = tenant

        in_pipelines = Mock()
        in_pipelines.value = [f'({pipeline1.name})']

        result = handle_query(api, pipelines=in_pipelines)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project.name: Project(
                            project.name,
                            project.url,
                            pipelines={
                                pipeline1.name: Pipeline(pipeline1.name)
                            }
                        )
                    }
                )
            },
            result.value
        )

    def test_get_all_jobs(self):
        """Checks the '--jobs" option.
        """
        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'
        job1.pipelines = Mock()
        job1.pipelines.return_value = []

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'
        job2.pipelines = Mock()
        job2.pipelines.return_value = []

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        job1.tenant = tenant
        job2.tenant = tenant

        in_jobs = Mock()
        in_jobs.value = None

        result = handle_query(api, jobs=in_jobs)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job1.name: Job(job1.name, job1.url),
                        job2.name: Job(job2.name, job1.url)
                    }
                )
            },
            result.value
        )

    def test_get_jobs_by_name(self):
        """Checks the '--jobs pattern1 pattern2" option.
        """
        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'
        job1.pipelines = Mock()
        job1.pipelines.return_value = []

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'
        job2.pipelines = Mock()
        job2.pipelines.return_value = []

        job3 = Mock()
        job3.name = 'job3'
        job3.url = 'url3'
        job3.pipelines = Mock()
        job3.pipelines.return_value = []

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2, job3]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        job1.tenant = tenant
        job2.tenant = tenant
        job3.tenant = tenant

        in_jobs = Mock()
        in_jobs.value = [f'({job1.name})']

        result = handle_query(api, jobs=in_jobs)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job1.name: Job(job1.name, job1.url)
                    }
                )
            },
            result.value
        )

    def test_get_jobs_by_url(self):
        """Checks the '--jobs --job_url pattern1 pattern2" option.
        """
        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'
        job1.pipelines = Mock()
        job1.pipelines.return_value = []

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'
        job2.pipelines = Mock()
        job2.pipelines.return_value = []

        job3 = Mock()
        job3.name = 'job3'
        job3.url = 'url3'
        job3.pipelines = Mock()
        job3.pipelines.return_value = []

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2, job3]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        job1.tenant = tenant
        job2.tenant = tenant
        job3.tenant = tenant

        in_jobs = Mock()
        in_jobs.value = None

        in_urls = Mock()
        in_urls.value = [f'({job1.url})']

        result = handle_query(api, jobs=in_jobs, job_url=in_urls)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job1.name: Job(job1.name, job1.url)
                    }
                )
            },
            result.value
        )

    def test_get_pipelines_through_jobs(self):
        """Checks that "--jobs" also returns the pipelines of the jobs.
        """
        pipeline1 = Mock()
        pipeline1.name = 'pipeline1'
        pipeline1.jobs = Mock()

        pipeline2 = Mock()
        pipeline2.name = 'pipeline2'
        pipeline2.jobs = Mock()

        pipeline3 = Mock()
        pipeline3.name = 'pipeline3'
        pipeline3.jobs = Mock()

        job = Mock()
        job.name = 'job1'
        job.url = 'url1'
        job.pipelines = Mock()
        job.pipelines.return_value = [pipeline1, pipeline2]

        project = Mock()
        project.name = 'project'
        project.url = 'url'
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline1, pipeline2, pipeline3]

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.projects = Mock()
        tenant.projects.return_value = [project]
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        project.tenant = tenant

        pipeline1.project = project
        pipeline2.project = project
        pipeline3.project = project

        pipeline1.jobs.return_value = [job]
        pipeline2.jobs.return_value = [job]
        pipeline3.jobs.return_value = []

        job.tenant = tenant

        in_jobs = Mock()
        in_jobs.value = None

        result = handle_query(api, jobs=in_jobs)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project.name: Project(
                            project.name,
                            project.url,
                            pipelines={
                                pipeline1.name: Pipeline(
                                    pipeline1.name,
                                    jobs={
                                        job.name: Job(job.name, job.url)
                                    }
                                ),
                                pipeline2.name: Pipeline(
                                    pipeline2.name,
                                    jobs={
                                        job.name: Job(job.name, job.url)
                                    }
                                )
                            }
                        )
                    },
                    jobs={
                        job.name: Job(job.name, job.url)
                    }
                )
            },
            result.value
        )

    def test_get_job_variants(self):
        """Checks the '--variants' options.
        """
        variant1 = {
            'parent': 'job1',
        }

        variant2 = {
            'parent': 'job2',
        }

        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'
        job1.pipelines = Mock()
        job1.pipelines.return_value = []
        job1.variants = Mock()
        job1.variants.return_value = [variant1]

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'
        job2.pipelines = Mock()
        job2.pipelines.return_value = []
        job2.variants = Mock()
        job2.variants.return_value = [variant2]

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.projects = Mock()
        tenant.projects.return_value = []
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        job1.tenant = tenant
        job2.tenant = tenant

        in_jobs = Mock()
        in_jobs.value = None

        result = handle_query(api, jobs=in_jobs, variants=None)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job1.name: Job(
                            job1.name, job1.url,
                            variants=[
                                Job.Variant.from_data(variant1)
                            ]
                        ),
                        job2.name: Job(
                            job2.name, job1.url,
                            variants=[
                                Job.Variant.from_data(variant2)
                            ]
                        )
                    }
                )
            },
            result.value
        )

    def test_get_all_builds(self):
        """Checks the '--builds' option.
        """
        build1 = DictMock()
        build1['uuid'] = 'build1'
        build1['result'] = 'SUCCESS'
        build1['duration'] = 1000

        build2 = DictMock()
        build2['uuid'] = 'build2'
        build2['result'] = 'SUCCESS'
        build2['duration'] = 1000

        job = Mock()
        job.name = 'job'
        job.url = 'url'
        job.builds = Mock()
        job.builds.return_value = [build1, build2]

        pipeline = Mock()
        pipeline.name = 'pipeline'
        pipeline.jobs = Mock()
        pipeline.jobs.return_value = [job]

        project = Mock()
        project.name = 'project'
        project.url = 'url'
        project.pipelines = Mock()
        project.pipelines.return_value = [pipeline]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant

        build1.job = job
        build2.job = job

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_builds = Mock()
        in_builds.value = None

        result = handle_query(api, builds=in_builds)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project.name: Project(
                            project.name,
                            project.url,
                            pipelines={
                                pipeline.name: Pipeline(
                                    pipeline.name,
                                    jobs={
                                        job.name: Job(
                                            job.name,
                                            job.url,
                                            {
                                                build1['uuid']: Build(
                                                    build1['uuid'],
                                                    build1['result'],
                                                    build1['duration']
                                                ),
                                                build2['uuid']: Build(
                                                    build2['uuid'],
                                                    build2['result'],
                                                    build2['duration']
                                                )
                                            }
                                        )
                                    }
                                )
                            }
                        )
                    }
                )
            },
            result.value
        )

    def test_get_builds_by_id(self):
        """Checks the '--builds pattern1 pattern2' option.
        """
        build1 = DictMock()
        build1['uuid'] = 'build1'
        build1['result'] = 'SUCCESS'
        build1['duration'] = 1000

        build2 = DictMock()
        build2['uuid'] = 'build2'
        build2['result'] = 'SUCCESS'
        build2['duration'] = 1000

        build3 = DictMock()
        build3['uuid'] = 'build3'
        build3['result'] = 'SUCCESS'
        build3['duration'] = 1000

        job = Mock()
        job.name = 'job'
        job.url = 'url'
        job.builds = Mock()
        job.builds.return_value = [build1, build2, build3]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant

        build1.job = job
        build2.job = job
        build3.job = job

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_builds = Mock()
        in_builds.value = [f"({build1['uuid']})"]

        result = handle_query(api, builds=in_builds)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job.name: Job(
                            job.name,
                            job.url,
                            {
                                build1['uuid']: Build(
                                    build1['uuid'],
                                    build1['result'],
                                    build1['duration']
                                )
                            }
                        )
                    }
                )
            },
            result.value
        )

    def test_get_builds_by_status(self):
        """Checks the '--builds --build-status pattern1 pattern2' option.
        """
        build1 = DictMock()
        build1['uuid'] = 'build1'
        build1['result'] = 'FAILURE'
        build1['duration'] = 1000

        build2 = DictMock()
        build2['uuid'] = 'build2'
        build2['result'] = 'SUCCESS'
        build2['duration'] = 1000

        build3 = DictMock()
        build3['uuid'] = 'build3'
        build3['result'] = 'FAILURE'
        build3['duration'] = 1000

        job = Mock()
        job.name = 'job'
        job.url = 'url'
        job.builds = Mock()
        job.builds.return_value = [build1, build2, build3]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant

        build1.job = job
        build2.job = job
        build3.job = job

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_builds = Mock()
        in_builds.value = None

        in_status = Mock()
        in_status.value = ['(SUCCESS)']

        result = handle_query(api, builds=in_builds, build_status=in_status)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job.name: Job(
                            job.name,
                            job.url,
                            {
                                build2['uuid']: Build(
                                    build2['uuid'],
                                    build2['result'],
                                    build2['duration']
                                )
                            }
                        )
                    }
                )
            },
            result.value
        )

    def test_get_last_build(self):
        """Checks the '--builds --last-build' option.
        """
        build1 = DictMock()
        build1['uuid'] = 'build1'
        build1['result'] = 'FAILURE'
        build1['duration'] = 1000

        build2 = DictMock()
        build2['uuid'] = 'build2'
        build2['result'] = 'SUCCESS'
        build2['duration'] = 1000

        build3 = DictMock()
        build3['uuid'] = 'build3'
        build3['result'] = 'FAILURE'
        build3['duration'] = 1000

        job = Mock()
        job.name = 'job'
        job.url = 'url'
        job.builds = Mock()
        job.builds.return_value = [build1, build2, build3]

        tenant = Mock()
        tenant.name = 'tenant'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job]

        job.tenant = tenant

        build1.job = job
        build2.job = job
        build3.job = job

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_builds = Mock()
        in_builds.value = None

        in_last = Mock()
        in_last.value = None

        result = handle_query(api, builds=in_builds, last_build=in_last)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    jobs={
                        job.name: Job(
                            job.name,
                            job.url,
                            {
                                build1['uuid']: Build(
                                    build1['uuid'],
                                    build1['result'],
                                    build1['duration']
                                )
                            }
                        )
                    }
                )
            },
            result.value
        )
