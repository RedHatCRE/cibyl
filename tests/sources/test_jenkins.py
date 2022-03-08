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
# pylint: disable=no-member
from unittest import TestCase
from unittest.mock import Mock

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.ci.system import System
from cibyl.sources.jenkins import Jenkins, JenkinsOSP, safe_request


def return_arg(query=None):
    """
        Helper function that returns its argument. It can't be a lambda because
        it will get called inside a decorated function
    """
    return {"jobs": query}


class TestSafeRequestJenkinsError(TestCase):
    """Tests for :func:`safe_request`."""

    def test_wraps_errors_jenkins_error(self):
        """Tests that errors coming out of the Jenkins API call are wrapped around the
        JenkinsError type.
        """

        @safe_request
        def request_test():
            raise Exception

        self.assertRaises(JenkinsError, request_test)

    def test_returns_result_when_no_error(self):
        """Tests that the call's output is returned when everything goes right.
        """
        result = {'some_key': 'some_value'}

        @safe_request
        def request_test():
            return result

        self.assertEqual(result, request_test())


class TestJenkinsSource(TestCase):
    """Tests for :class:`Jenkins`."""

    def setUp(self):
        self.jenkins = Jenkins("url", "user", "token")

    # pylint: disable=protected-access
    def test_with_all_args(self):
        """Checks that the object is built correctly when all arguments are
        provided.
        """
        url = 'url/to/jenkins/'
        username = 'user'
        cert = 'path/to/cert.pem'
        token = 'token'

        jenkins = Jenkins(url, username, token, cert)

        self.assertEqual(cert, jenkins.client._session.verify)

    def test_with_no_cert(self):
        """Checks that object is built correctly when the certificate is not
        provided.
        """
        url = 'url/to/jenkins/'
        username = 'user'
        cert = None
        token = 'token'

        jenkins = Jenkins(url, username, token, cert)

        self.assertIsNone(jenkins.client._session.verify)

    def test_get_jobs(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_jobs` is
            correct. The jenkins API method that should do the query is mocked
            to that it returns the query itself.
        """
        self.jenkins.client.get_info = Mock()
        self.jenkins.client.get_info.side_effect = return_arg

        jobs_builds = self.jenkins.get_jobs(True)
        jobs = self.jenkins.get_jobs(False)
        self.assertEqual(jobs_builds, self.jenkins.jobs_builds_query)
        self.assertEqual(jobs, self.jenkins.jobs_query)

    def test_populate_jobs_without_builds(self):
        """
            Tests that the jenkins info is correctly parsed and job models are
            populated.
        """
        jobs = [{"_class": "job", "name": "job1", "url": "url1"},
                {"_class": "job", "name": "job2", "url": "url2"},
                {"_class": "job", "name": "job3", "url": "url3"}]
        system = System("test_system", "test")
        self.jenkins.populate_jobs(system, jobs)
        self.assertEqual(3, len(system.jobs.value))
        self.assertEqual("job1", system.jobs.value[0].name.value)
        self.assertEqual("job2", system.jobs.value[1].name.value)
        self.assertEqual("job3", system.jobs.value[2].name.value)
        self.assertEqual("url1", system.jobs.value[0].url.value)
        self.assertEqual("url2", system.jobs.value[1].url.value)
        self.assertEqual("url3", system.jobs.value[2].url.value)

    def test_populate_jobs_with_builds(self):
        """
            Tests that the jenkins info is correctly parsed and job and build
            models are correctly populated.
        """
        jobs = [{'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                 'name': 'job1', 'url': 'url1',
                 'builds': [
                     {'_class': 'org.jenkinsci.plugins.workflow.job.',
                      'number': 13, 'result': 'FAILURE'},
                     {'_class': 'org.jenkinsci.plugins.workflow.job',
                      'number': 10, 'result': 'SUCCESS'}]},
                {'_class': 'jenkins.branch.OrganizationFolder',
                 'name': 'ccc',
                 'url': 'url2'},
                {'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                 'name': 'job3', 'url': 'url3',
                 'builds': [
                     {'_class': 'org.jenkinsci.plugins.workflow.job',
                      'number': 2, 'result': 'SUCCESS'}]}
                ]

        system = System("test_system", "test")
        self.jenkins.populate_jobs(system, jobs)

        self.assertEqual(2, len(system.jobs.value))
        job1 = system.jobs.value[0]
        job2 = system.jobs.value[1]
        self.assertEqual("job1", job1.name.value)
        self.assertEqual("job3", job2.name.value)
        self.assertEqual("url1", job1.url.value)
        self.assertEqual("url3", job2.url.value)

        self.assertEqual(2, len(job1.builds.value))
        self.assertEqual("13", job1.builds.value[0].build_id.value)
        self.assertEqual("FAILURE", job1.builds.value[0].status.value)
        self.assertEqual("10", job1.builds.value[1].build_id.value)
        self.assertEqual("SUCCESS", job1.builds.value[1].status.value)

        self.assertEqual(1, len(job2.builds.value))
        self.assertEqual("2", job2.builds.value[0].build_id.value)
        self.assertEqual("SUCCESS", job2.builds.value[0].status.value)


class TestJenkinsOSPSource(TestCase):
    """Tests for :class:`Jenkins`.
    """

    # pylint: disable=protected-access
    def test_with_all_args(self):
        """Checks that the object is built correctly when all arguments are
        provided.
        """
        url = 'url/to/jenkins/'
        username = 'user'
        cert = 'path/to/cert.pem'
        token = 'token'

        jenkins = JenkinsOSP(url, username, token, cert)

        self.assertEqual(cert, jenkins.client._session.verify)

    def test_with_no_cert(self):
        """Checks that object is built correctly when the certificate is not
        provided.
        """
        url = 'url/to/jenkins/'
        username = 'user'
        cert = None
        token = 'token'

        jenkins = JenkinsOSP(url, username, token, cert)

        self.assertIsNone(jenkins.client._session.verify)
