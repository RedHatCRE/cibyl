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
import json
from unittest import TestCase
from unittest.mock import Mock, patch

from cibyl.exceptions.jenkins import JenkinsError
from cibyl.sources.jenkins import (Jenkins, filter_builds, filter_jobs,
                                   safe_request)


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
                    {'_class': 'empty', 'name': 'ansible-empty'}]}
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
        self.assertEqual(builds_found["1"].build_id.value, "1")
        self.assertEqual(builds_found["1"].status.value, "SUCCESS")
        self.assertEqual(builds_found["2"].build_id.value, "2")
        self.assertEqual(builds_found["2"].status.value, "FAILURE")

    def test_get_last_build(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_last_build`
        is correct.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1',
                              'lastBuild': {'number': 1, 'result': "SUCCESS"}
                              }]}
        self.jenkins.send_request = Mock(side_effect=[response])

        jobs = self.jenkins.get_last_build()
        self.assertEqual(len(jobs), 1)
        job = jobs["ansible"]
        self.assertEqual(job.name.value, "ansible")
        self.assertEqual(job.url.value, "url1")
        self.assertEqual(len(job.builds.value), 1)
        build = job.builds.value["1"]
        self.assertEqual(build.build_id.value, "1")
        self.assertEqual(build.status.value, "SUCCESS")

    def test_get_last_build_job_no_builds(self):
        """Test that get_last_build handles properly a job has no builds."""

        response = {'jobs': [{'_class': 'org.job.WorkflowJob',
                              'name': 'ansible-nfv-branch', 'url': 'url',
                              'lastBuild': None},
                             {'_class': 'folder'}]}

        self.jenkins.send_request = Mock(side_effect=[response])

        jobs = self.jenkins.get_last_build()
        self.assertEqual(len(jobs), 1)
        job = jobs["ansible-nfv-branch"]
        self.assertEqual(job.name.value, "ansible-nfv-branch")
        self.assertEqual(job.url.value, "url")
        self.assertEqual(len(job.builds.value), 0)

    @patch("requests.get")
    def test_send_request(self, patched_get):
        """
            Test that send_request method parses the response correctly.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        patched_get.return_value = Mock(text=json.dumps(response))
        self.assertEqual(response, self.jenkins.send_request("test"))
        patched_get.assert_called_with("url//api/jsontest",
                                       verify=self.jenkins.cert,
                                       timeout=None)


class TestFilters(TestCase):
    """Tests for filter functions in jenkins source module."""
    def test_filter_jobs(self):
        """
            Test that filter_jobs filters the jobs given the user input.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        args = Mock()
        args.value = ["ans"]
        jobs_filtered = filter_jobs(response, jobs=args)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}},
                    ]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_job_name_job_url(self):
        """
            Test that filter_jobs filters the jobs given the user input.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        job_name = Mock()
        job_name.value = ["ans2"]
        job_url = Mock()
        job_url.value = ["url3"]
        jobs_filtered = filter_jobs(response, job_name=job_name,
                                    job_url=job_url)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_job_name(self):
        """
            Test that filter_jobs filters the jobs given the user input.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        job_name = Mock()
        job_name.value = ["ansible"]
        jobs_filtered = filter_jobs(response, job_name=job_name)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}}]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_job_url(self):
        """
            Test that filter_jobs filters the jobs given the user input.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}
                    ]
        job_url = Mock()
        job_url.value = ["url2"]
        jobs_filtered = filter_jobs(response, job_url=job_url)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}}]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_job_name_job_url_jobs(self):
        """
            Test that filter_jobs filters the jobs given the user input.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        args = Mock()
        args.value = ["ans"]
        job_name = Mock()
        job_name.value = ["ansible"]
        job_url = Mock()
        job_url.value = ["url1"]
        jobs_filtered = filter_jobs(response, jobs=args, job_url=job_url,
                                    job_name=job_name)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}}]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_builds_builds_build_id_build_status_empty(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = []
        build_id = Mock()
        build_id.value = ["3"]
        build_status = Mock()
        build_status.value = ["failure"]
        builds_filtered = filter_builds(response, builds=builds,
                                        build_status=build_status,
                                        build_id=build_id)
        expected = []
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_builds_build_id_build_status(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = []
        build_id = Mock()
        build_id.value = ["3"]
        build_status = Mock()
        build_status.value = ["success"]
        builds_filtered = filter_builds(response, builds=builds,
                                        build_status=build_status,
                                        build_id=build_id)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_builds_build_id(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = []
        build_id = Mock()
        build_id.value = ["3"]
        builds_filtered = filter_builds(response, builds=builds,
                                        build_id=build_id)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'FAILURE'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_builds_build_status(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = []
        build_status = Mock()
        build_status.value = ["success"]
        builds_filtered = filter_builds(response, builds=builds,
                                        build_status=build_status)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_build_id_build_status(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        build_id = Mock()
        build_id.value = ["3"]
        build_status = Mock()
        build_status.value = ["success"]
        builds_filtered = filter_builds(response,
                                        build_status=build_status,
                                        build_id=build_id)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_builds(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = []
        builds_filtered = filter_builds(response, builds=builds)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "4",
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_build_status(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        build_status = Mock()
        build_status.value = ["success"]
        builds_filtered = filter_builds(response,
                                        build_status=build_status)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_build_id(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        build_id = Mock()
        build_id.value = ["3"]
        builds_filtered = filter_builds(response,
                                        build_id=build_id)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'}]
        self.assertEqual(builds_filtered, expected)
