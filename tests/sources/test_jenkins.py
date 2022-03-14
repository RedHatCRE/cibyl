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
from cibyl.sources.jenkins import Jenkins, safe_request


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

        self.assertEqual(cert, jenkins.cert)

    def test_with_no_cert(self):
        """Checks that object is built correctly when the certificate is not
        provided.
        """
        url = 'url/to/jenkins/'
        username = 'user'
        cert = None
        token = 'token'

        jenkins = Jenkins(url, username, token, cert)

        self.assertIsNone(jenkins.cert)

    def test_get_jobs_all(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_jobs` is
            correct.
        """
        self.jenkins.send_request = Mock(return_value={"jobs": []})
        jobs_arg = Mock()
        jobs_arg.value = []

        jobs = self.jenkins.get_jobs(jobs=jobs_arg)
        self.jenkins.send_request.assert_called_with(
                                self.jenkins.jobs_query)
        self.assertEqual(len(jobs), 0)

    def test_get_jobs(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_jobs` is
            correct.
        """
        response = {"jobs": [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'},
                    {'_class': 'org..job.WorkflowRun', 'name': "job2",
                     'url': 'url2'},
                    {'_class': 'empty', 'name': 'empty'}]}
        self.jenkins.send_request = Mock(return_value=response)
        jobs_arg = Mock()
        jobs_arg.value = ["ansible"]

        jobs = self.jenkins.get_jobs(jobs=jobs_arg)
        self.assertEqual(len(jobs), 1)
        self.assertTrue("ansible" in jobs)
        self.assertEqual(jobs["ansible"].name.value, "ansible")
        self.assertEqual(jobs["ansible"].url.value, "url1")

    def test_get_builds(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_builds` is
            correct.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': "SUCCESS"},
                                {'number': 2, 'result': "FAILURE"}]}
        self.jenkins.send_request = Mock(side_effect=[response, builds])

        jobs = self.jenkins.get_builds()
        self.assertEqual(len(jobs), 1)
        job = jobs["ansible"]
        self.assertEqual(job.name.value, "ansible")
        self.assertEqual(job.url.value, "url1")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 2)
        self.assertEqual(builds_found[0].build_id.value, "1")
        self.assertEqual(builds_found[0].status.value, "SUCCESS")
        self.assertEqual(builds_found[1].build_id.value, "2")
        self.assertEqual(builds_found[1].status.value, "FAILURE")
