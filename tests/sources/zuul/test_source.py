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
from cibyl.sources.zuul.api import ZuulAPIError
from cibyl.sources.zuul.source import Zuul


class TestZuulConnect(TestCase):
    """Tests the 'connect' function on the Zuul source.
    """

    def assert_not_raises(self, exception_type, call):
        """Verifies that an undesired exception does not come out of
        a certain function.

        :param exception_type: The type of the undesired exception.
        :param call: The call to check.
        """
        try:
            call()
        except exception_type:
            self.fail('Unexpected exception.')

    def test_connect_success(self):
        """Checks that nothing happens if the host can be connected to.
        """

        def successful_connection():
            return

        api = Mock()
        api.info = Mock()
        api.info.side_effect = successful_connection

        zuul = Zuul(api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        self.assert_not_raises(ZuulAPIError, zuul.connect)

        api.info.assert_called()

    def test_error_when_connect_fails(self):
        """Checks that a :class:`ZuulAPIError` is thrown when connection to
        the host could not be made.
        """

        def failed_connection():
            raise ZuulAPIError

        api = Mock()
        api.info = Mock()
        api.info.side_effect = failed_connection

        zuul = Zuul(api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        self.assertRaises(ZuulAPIError, zuul.connect)


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
        job1 = 'job_1'
        job2 = 'job_2'

        url = 'localhost:8080/zuul'

        kwargs = {
            'jobs': Argument('name', list, '', value=[])
        }

        def build_url(tenant, job):
            return f"{url}/t/{tenant.name}/job/{job}"

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

        self.tenants[0].name = 'tenant1'
        self.tenants[1].name = 'tenant2'

        self.tenants[0].jobs.return_value = [{'name': job1}]
        self.tenants[1].jobs.return_value = [{'name': job2}]

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

        self.tenants[0].name.value = 'tenant1'
        self.tenants[1].name.value = 'tenant2'

        self.tenants[0].jobs.return_value = [{'name': job1}]
        self.tenants[1].jobs.return_value = [{'name': job2}, {'name': job3}]

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

        self.tenants[0].jobs.return_value = [{'name': job1}]
        self.tenants[1].jobs.return_value = [{'name': job2}]

        self.tenants[0].builds.return_value = [
            {'uuid': build1, 'job_name': job1, 'result': 'success'}
        ]
        self.tenants[1].builds.return_value = [
            {'uuid': build2, 'job_name': job2, 'result': 'success'}
        ]

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

        self.tenants[0].jobs.return_value = [{'name': job1}]
        self.tenants[1].jobs.return_value = [{'name': job2}]

        self.tenants[0].builds.return_value = [
            {'uuid': build1, 'job_name': job1, 'result': 'success'}
        ]
        self.tenants[1].builds.return_value = [
            {'uuid': build2, 'job_name': job2, 'result': 'success'}
        ]

        zuul = Zuul(self.api, 'zuul-ci', 'zuul', 'http://localhost:8080')

        result = zuul.get_builds(**kwargs).value

        self.assertEqual([job1], list(result.keys()))

        self.assertEqual([build1], list(result[job1].builds.keys()))

        self.assertEqual(build1, result[job1].builds[build1].build_id.value)
