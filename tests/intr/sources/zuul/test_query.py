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
from cibyl.models.ci.job import Job
from cibyl.models.ci.project import Project
from cibyl.models.ci.tenant import Tenant
from cibyl.sources.zuul.query import handle_query


class DictMock(Mock):
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
        """Checks the '--tenant name1 name2' option.
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
        in_tenants.value = [tenant1.name]

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

        project2 = Mock()
        project2.name = 'project2'

        tenant = Mock()
        tenant.name = 'tenant'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_projects = Mock()
        in_projects.value = None

        result = handle_query(api, projects=in_projects)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project1.name: Project(project1.name),
                        project2.name: Project(project2.name)
                    }
                )
            },
            result.value
        )

    def test_get_projects_by_name(self):
        """Checks the '--projects name1 name2' option.
        """
        project1 = Mock()
        project1.name = 'project1'

        project2 = Mock()
        project2.name = 'project2'

        tenant = Mock()
        tenant.name = 'tenant'

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_projects = Mock()
        in_projects.value = [project1.name]

        result = handle_query(api, projects=in_projects)

        self.assertEqual(
            {
                tenant.name: Tenant(
                    tenant.name,
                    projects={
                        project1.name: Project(project1.name)
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

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

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
        """Checks the '--jobs name1 name2" option.
        """
        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'

        job3 = Mock()
        job3.name = 'job3'
        job3.url = 'url3'

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2, job3]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_jobs = Mock()
        in_jobs.value = [job1.name]

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
        """Checks the '--jobs --job_url url1 url2" option.
        """
        job1 = Mock()
        job1.name = 'job1'
        job1.url = 'url1'

        job2 = Mock()
        job2.name = 'job2'
        job2.url = 'url2'

        job3 = Mock()
        job3.name = 'job3'
        job3.url = 'url3'

        tenant = Mock()
        tenant.name = 'tenant1'
        tenant.jobs = Mock()
        tenant.jobs.return_value = [job1, job2, job3]

        api = Mock()
        api.tenants = Mock()
        api.tenants.return_value = [tenant]

        in_jobs = Mock()
        in_jobs.value = None

        in_urls = Mock()
        in_urls.value = [job1.url]

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
            },
            result.value
        )

    def test_get_builds_by_id(self):
        """Checks the '--builds id1 id2' option.
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
        in_builds.value = [build1['uuid']]

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
        """Checks the '--builds --build-status' option.
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
        in_status.value = ['SUCCESS']

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
