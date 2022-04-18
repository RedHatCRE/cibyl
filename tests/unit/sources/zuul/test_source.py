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
from cibyl.models.ci.job import Job
from cibyl.sources.zuul.source import Zuul


class TestZuulGetJobs(TestCase):
    """Tests the 'get_jobs' method on :class:`Zuul`.
    """

    def setUp(self):
        def new_mocked_tenant():
            tenant = Mock()
            tenant.jobs = Mock()
            tenant.jobs.return_value = []

            return tenant

        self.tenants = [
            new_mocked_tenant(),
            new_mocked_tenant()
        ]

        self.api = Mock()
        self.api.tenants = Mock()
        self.api.tenants.return_value = self.tenants

    def test_calls(self):
        """Checks that the source invokes all necessary calls to retrieve
        the jobs.
        """
        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        zuul.get_jobs()

        self.api.tenants.assert_called()

        for tenant in self.tenants:
            tenant.jobs.assert_called()

    def test_returned_attribute(self):
        """Checks the correct format of the returned attribute dictionary.
        """
        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_jobs()

        self.assertEqual('jobs', result.name)
        self.assertEqual(Job, result.attr_type)

    def test_all_jobs_retrieved(self):
        """Checks that the source is capable of retrieving all jobs on the
        remote alongside their appropriate data.
        """

        def build_url(tenant, job):
            return f"{url}/t/{tenant.name}/job/{job}"

        job1 = 'job_1'
        job2 = 'job_2'

        url = 'localhost:8080/zuul'

        kwargs = {
            'jobs': Argument('name', list, '', value=[])
        }

        expected_jobs = {
            job1: Job(
                name=job1,
                url=build_url(self.tenants[0], job1)
            ),
            job2: Job(
                name=job2,
                url=build_url(self.tenants[1], job2)
            )
        }

        client1 = Mock()
        client2 = Mock()

        client1.name = job1
        client2.name = job2

        self.tenants[0].name = 'tenant1'
        self.tenants[1].name = 'tenant2'

        self.tenants[0].jobs.return_value = [client1]
        self.tenants[1].jobs.return_value = [client2]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', url)

        result = zuul.get_jobs(**kwargs).value

        # Check that the desired data was obtained from the jobs
        self.assertEqual(expected_jobs, result)

    def test_searched_job_is_retrieved(self):
        """Checks that the source is capable of retrieving just some
        specific jobs.
        """

        job1 = 'job_1'
        job2 = 'job_2'
        job3 = 'job_3'

        kwargs = {
            'jobs': Argument('name', list, '', value=[job1, job2])
        }

        client1 = Mock()
        client2 = Mock()
        client3 = Mock()

        client1.name = job1
        client2.name = job2
        client3.name = job3

        self.tenants[0].name.value = 'tenant1'
        self.tenants[1].name.value = 'tenant2'

        self.tenants[0].jobs.return_value = [client1]
        self.tenants[1].jobs.return_value = [client2, client3]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        # Check that just the desired jobs where retrieved
        result = zuul.get_jobs(**kwargs).value

        self.assertEqual(kwargs['jobs'].value, list(result.keys()))


class TestZuulGetBuilds(TestCase):
    """Tests the get_builds method on the Zuul source.
    """

    def setUp(self):
        def new_mocked_tenant():
            tenant = Mock()
            tenant.jobs = Mock()
            tenant.jobs.return_value = []
            tenant.builds = Mock()
            tenant.builds.return_value = []

            return tenant

        self.tenants = [
            new_mocked_tenant(),
            new_mocked_tenant()
        ]

        self.api = Mock()
        self.api.tenants = Mock()
        self.api.tenants.return_value = self.tenants

    def test_higher_level_type_is_returned(self):
        """Checks that builds are returned as part of a job collection,
        following the idea that requests should always try to provide
        information of the highest possible level.
        """
        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds()

        self.assertEqual('jobs', result.name)
        self.assertEqual(Job, result.attr_type)

    def test_all_builds_retrieved(self):
        """Checks that the source is capable of retrieving all builds
        on the remote alongside their appropriate data."""
        build1 = '1'
        build2 = '2'

        job1 = 'job1'
        job2 = 'job2'

        kwargs = {
            'jobs': Argument('name', list, '', value=[])
        }

        client1 = Mock()
        client2 = Mock()

        client1.name = job1
        client2.name = job2

        client1.builds = Mock()
        client2.builds = Mock()

        client1.builds.return_value = [
            {
                'uuid': build1,
                'job_name': job1,
                'result': 'success'
            }
        ]

        client2.builds.return_value = [
            {
                'uuid': build2,
                'job_name': job2,
                'result': 'success'
            }
        ]

        self.tenants[0].jobs.return_value = [client1]
        self.tenants[1].jobs.return_value = [client2]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        self.assertEqual([job1, job2], list(result.keys()))

        self.assertEqual([build1], list(result[job1].builds.keys()))
        self.assertEqual([build2], list(result[job2].builds.keys()))

        self.assertEqual(build1, result[job1].builds[build1].build_id.value)
        self.assertEqual(build2, result[job2].builds[build2].build_id.value)

    def test_builds_for_searched_jobs_are_retrieved(self):
        """Checks that only the builds belonging to the requested jobs
        are retrieved.
        """
        build1 = '1'
        build2 = '2'

        job1 = 'job1'
        job2 = 'job2'

        kwargs = {
            'jobs': Argument('name', list, '', value=[job1])
        }

        client1 = Mock()
        client2 = Mock()

        client1.name = job1
        client2.name = job2

        client1.builds = Mock()
        client2.builds = Mock()

        client1.builds.return_value = [
            {
                'uuid': build1,
                'job_name': job1,
                'result': 'success'
            }
        ]

        client2.builds.return_value = [
            {
                'uuid': build2,
                'job_name': job2,
                'result': 'success'
            }
        ]

        self.tenants[0].jobs.return_value = [client1]
        self.tenants[1].jobs.return_value = [client2]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        self.assertEqual([job1], list(result.keys()))

        self.assertEqual([build1], list(result[job1].builds.keys()))

        self.assertEqual(build1, result[job1].builds[build1].build_id.value)


class TestGetLastBuild(TestCase):
    """Tests the 'get_last_build' method on :class:`Zuul`.
    """

    def setUp(self):
        def new_mocked_tenant():
            tenant = Mock()
            tenant.jobs = Mock()
            tenant.jobs.return_value = []
            tenant.builds = Mock()
            tenant.builds.return_value = []

            return tenant

        self.tenants = [
            new_mocked_tenant(),
            new_mocked_tenant()
        ]

        self.api = Mock()
        self.api.tenants = Mock()
        self.api.tenants.return_value = self.tenants

    def test_gets_only_the_most_recent_build(self):
        """Checks that only the latest build is returned for the
        '--last-build' flag.
        """
        build1 = '1'
        build2 = '2'

        job = 'job'

        kwargs = {
            'jobs': Argument('name', list, '', value=[]),
            'last_build': None
        }

        client1 = Mock()
        client1.name = job
        client1.builds = Mock()
        client1.builds.return_value = [
            {
                'uuid': build1,
                'job_name': job,
                'result': 'success'
            },
            {
                'uuid': build2,
                'job_name': job,
                'result': 'success'
            }
        ]

        self.tenants[0].jobs.return_value = [client1]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        # Check that the job was returned
        self.assertEqual([job], list(result.keys()))

        # Assert build 2 was filtered out
        self.assertEqual([build1], list(result[job].builds.keys()))

        # Verify that build order was respected
        self.assertEqual(build1, result[job].builds[build1].build_id.value)


class TestBuildFilters(TestCase):
    """Tests for all filters that apply to builds.
    """

    def setUp(self):
        def new_mocked_tenant():
            tenant = Mock()
            tenant.jobs = Mock()
            tenant.jobs.return_value = []
            tenant.builds = Mock()
            tenant.builds.return_value = []

            return tenant

        self.tenants = [
            new_mocked_tenant(),
            new_mocked_tenant()
        ]

        self.api = Mock()
        self.api.tenants = Mock()
        self.api.tenants.return_value = self.tenants

    def test_filters_by_build_id(self):
        """Checks that only those builds which IDs are among the ones
        entered in '--build-id' are returned.
        """
        build1 = '1'
        build2 = '2'
        build3 = '3'

        job = 'job'

        kwargs = {
            'jobs': Argument('name', list, '', value=[]),
            'build_id': Argument('uuid', list, '', value=[build1, build3])
        }

        client1 = Mock()
        client1.name = job
        client1.builds = Mock()
        client1.builds.return_value = [
            {
                'uuid': build1,
                'result': '---'
            },
            {
                'uuid': build2,
                'result': '---'
            },
            {
                'uuid': build3,
                'result': '---'
            }
        ]

        self.tenants[0].jobs.return_value = [client1]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        # Check that the job was returned
        self.assertEqual([job], list(result.keys()))

        # Assert build 2 was filtered
        self.assertEqual([build1, build3], list(result[job].builds.keys()))

        # Verify that passed builds have the desired ID
        self.assertIn(result[job].builds[build1].build_id.value, build1)
        self.assertIn(result[job].builds[build3].build_id.value, build3)

    def test_filters_by_build_status(self):
        """Checks that only those builds which status is among the ones
        entered in '--build-status' are returned.
        """
        build1 = '1'
        build2 = '2'
        build3 = '3'

        job = 'job'

        status_ok = 'OK'
        status_not_ok = 'NOT_OK'

        status = [status_ok, status_not_ok]

        kwargs = {
            'jobs': Argument('name', list, '', value=[]),
            'build_status': Argument('status', list, '', value=status)
        }

        client1 = Mock()
        client1.name = job
        client1.builds = Mock()
        client1.builds.return_value = [
            {
                'uuid': build1,
                'result': status_ok
            },
            {
                'uuid': build2,
                'result': '---'
            },
            {
                'uuid': build3,
                'result': status_not_ok
            }
        ]

        self.tenants[0].jobs.return_value = [client1]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        # Check that the job was returned
        self.assertEqual([job], list(result.keys()))

        # Assert build 2 was filtered
        self.assertEqual([build1, build3], list(result[job].builds.keys()))

        # Verify that passed builds have the desired status
        self.assertIn(result[job].builds[build1].status.value, status)
        self.assertIn(result[job].builds[build3].status.value, status)
