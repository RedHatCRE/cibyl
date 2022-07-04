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
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.exceptions.source import MissingArgument, SourceException
from cibyl.sources.jenkins import (Jenkins, filter_builds, filter_jobs,
                                   get_build_filters, safe_request)


class TestSafeRequestJenkinsError(TestCase):
    """Tests for :func:`safe_request`."""

    def test_wraps_errors_jenkins_error(self):
        """Tests that errors coming out of the Jenkins API call
        are wrapped around the JenkinsError type.
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
                    {'_class': 'folder', 'name': 'ansible-empty'}]}
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

    def test_get_builds_job_filtered(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_builds` is
            correct and it filters out jobs that have no builds.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'},
                             {'_class': 'org..job.WorkflowRun',
                              'name': "missing", 'url': 'url1'}]}
        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': "SUCCESS"},
                                {'number': 2, 'result': "FAILURE"}]}
        builds2 = {'_class': '_empty',
                   'allBuilds': [{'number': 1, 'result': "UNSTABLE"},
                                 {'number': 2, 'result': "UNSTABLE"}]}
        self.jenkins.send_request = Mock(side_effect=[response, builds,
                                                      builds2])

        build_arg = Argument("build_status", arg_type=str, description="",
                             value=["success"])
        jobs = self.jenkins.get_builds(build_status=build_arg)
        self.assertEqual(len(jobs), 1)
        job = jobs["ansible"]
        self.assertEqual(job.name.value, "ansible")
        self.assertEqual(job.url.value, "url1")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found["1"].build_id.value, "1")
        self.assertEqual(builds_found["1"].status.value, "SUCCESS")

    def test_get_builds_jobs_without_builds_kep(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_builds` is
            correct and it keeps jobs that have no builds when no filtering is
            done.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'},
                             {'_class': 'org..job.WorkflowRun',
                              'name': "missing", 'url': 'url1'}]}
        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': "SUCCESS"},
                                {'number': 2, 'result': "FAILURE"}]}
        self.jenkins.send_request = Mock(side_effect=[response, builds,
                                                      None])

        build_arg = Argument("build_status", arg_type=str, description="",
                             value=[])
        jobs = self.jenkins.get_builds(build_status=build_arg)
        self.assertEqual(len(jobs), 2)
        job = jobs["ansible"]
        self.assertEqual(job.name.value, "ansible")
        self.assertEqual(job.url.value, "url1")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 2)
        self.assertEqual(builds_found["1"].build_id.value, "1")
        self.assertEqual(builds_found["1"].status.value, "SUCCESS")
        self.assertEqual(builds_found["2"].build_id.value, "2")
        self.assertEqual(builds_found["2"].status.value, "FAILURE")
        job = jobs["missing"]
        self.assertEqual(job.name.value, "missing")
        self.assertEqual(job.url.value, "url1")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 0)

    def test_get_builds_with_stages(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_builds` is
            correct when requesting stages.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': "SUCCESS"},
                                {'number': 2, 'result': "FAILURE"}]}
        stages1 = {'stages': [{'name': 'build1', 'status': 'SUCCESS'},
                              {'name': 'run1', 'status': 'FAILURE'}]}
        stages2 = {'stages': [{'name': 'build2', 'status': 'FAILURE'},
                              {'name': 'run2', 'status': 'SUCCESS'}]}
        self.jenkins.send_request = Mock(side_effect=[response, builds,
                                                      stages1, stages2])

        jobs = self.jenkins.get_builds(stages=[])
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
        stages = builds_found["1"].stages.value
        self.assertEqual(len(stages), 2)
        self.assertEqual(stages[0].name.value, "build1")
        self.assertEqual(stages[0].status.value, "SUCCESS")
        self.assertEqual(stages[1].name.value, "run1")
        self.assertEqual(stages[1].status.value, "FAILURE")
        stages = builds_found["2"].stages.value
        self.assertEqual(len(stages), 2)
        self.assertEqual(stages[0].name.value, "build2")
        self.assertEqual(stages[0].status.value, "FAILURE")
        self.assertEqual(stages[1].name.value, "run2")
        self.assertEqual(stages[1].status.value, "SUCCESS")

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

    def test_get_last_build_filter_jobs(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_last_build`
        is correct and it filters jobs that do not have any build matching the
        criteria.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1',
                              'lastBuild': {'number': 1, 'result': "SUCCESS"}
                              }]}
        self.jenkins.send_request = Mock(side_effect=[response])

        build_arg = Argument("build_status", arg_type=str, description="",
                             value=["failure"])
        jobs = self.jenkins.get_last_build(build_status=build_arg)
        self.assertEqual(len(jobs), 0)

    def test_get_last_build_with_stages(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_last_build`
        with stages is correct.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1',
                              'lastBuild': {'number': 1, 'result': "SUCCESS"}
                              }]}
        stages = {'stages': [{'name': 'build1', 'status': 'SUCCESS'},
                             {'name': 'run1', 'status': 'FAILURE'}]}
        self.jenkins.send_request = Mock(side_effect=[response, stages])

        jobs = self.jenkins.get_last_build(stages=[])
        self.assertEqual(len(jobs), 1)
        job = jobs["ansible"]
        self.assertEqual(job.name.value, "ansible")
        self.assertEqual(job.url.value, "url1")
        self.assertEqual(len(job.builds.value), 1)
        build = job.builds.value["1"]
        self.assertEqual(build.build_id.value, "1")
        self.assertEqual(build.status.value, "SUCCESS")
        stages = build.stages.value
        self.assertEqual(len(stages), 2)
        self.assertEqual(stages[0].name.value, "build1")
        self.assertEqual(stages[0].status.value, "SUCCESS")
        self.assertEqual(stages[1].name.value, "run1")
        self.assertEqual(stages[1].status.value, "FAILURE")

    def test_get_stages(self):
        """
            Tests that the internal logic from :meth:`Jenkins._get_stages`
             with stages is correct.
        """
        response = {'stages': [{'name': 'build1', 'status': 'SUCCESS'},
                               {'name': 'run1', 'status': 'FAILURE'}]}
        self.jenkins.send_request = Mock(side_effect=[response])
        stages = self.jenkins._get_stages("job", "build")
        query = "/job/build/wfapi/describe"
        self.jenkins.send_request.assert_called_once_with(query=query,
                                                          api_entrypoint="",
                                                          item="job")
        self.assertEqual(len(stages), 2)
        self.assertEqual(stages[0].name.value, "build1")
        self.assertEqual(stages[0].status.value, "SUCCESS")
        self.assertEqual(stages[1].name.value, "run1")
        self.assertEqual(stages[1].status.value, "FAILURE")

    def test_get_stages_no_stages(self):
        """
            Tests that the internal logic from :meth:`Jenkins._get_stages`
             with no stages is correct.
        """
        response = {'stages': None}
        self.jenkins.send_request = Mock(side_effect=[response])
        self.assertIsNone(self.jenkins._get_stages("job", "build"))

    def test_get_last_build_from_get_builds(self):
        """
        Test that get_last_build is called when calling get_builds with
        --last-build option.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1',
                              'lastBuild': {'number': 1, 'result': "SUCCESS"}
                              }]}
        self.jenkins.send_request = Mock(side_effect=[response])
        arg = Mock()
        arg.value = []

        jobs = self.jenkins.get_builds(last_build=arg)
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

    def test_get_tests(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 3)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1000)
        self.assertEqual(tests_found['test2'].result.value, 'SKIPPED')
        self.assertEqual(tests_found['test2'].class_name.value, 'class2')
        self.assertEqual(tests_found['test2'].duration.value, 0)
        self.assertEqual(tests_found['test3'].result.value, 'FAILED')
        self.assertEqual(tests_found['test3'].class_name.value, 'class2')
        self.assertEqual(tests_found['test3'].duration.value, 2400)

    def test_get_tests_no_completed_build(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when there is no completed build.
        """

        response = {'jobs': [{'_class': 'org.job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty', 'allBuilds': []}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=[])

        self.jenkins.send_request = Mock(side_effect=[response, builds])

        jobs = self.jenkins.get_tests(builds=build_kwargs)
        self.assertEqual(len(jobs), 1)
        builds_found = jobs['ansible'].builds.value
        self.assertEqual(len(builds_found), 0)

    def test_get_tests_for_specific_build(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when a specific build is set.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}
        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}
        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': 'class1', 'duration': 1.1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 7.2,
                         'name': 'test2', 'status': 'PASSED'}]}]}

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        # Mock the --build command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])

        jobs = self.jenkins.get_tests(builds=build_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 2)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1100)
        self.assertEqual(tests_found['test2'].result.value, 'PASSED')
        self.assertEqual(tests_found['test2'].class_name.value, 'class2')
        self.assertEqual(tests_found['test2'].duration.value, 7200)

    def test_get_tests_multiple_jobs(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when multiple jobs match.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1',
                              'lastBuild': {'number': 1, 'result': 'SUCCESS'}},
                             {'_class': 'org..job.WorkflowRun',
                              'name': 'ansible-two', 'url': 'url2',
                              'lastBuild': {'number': 27,
                                            'result': 'SUCCESS'}}]}
        tests1 = {'_class': '_empty',
                  'suites': [
                    {'cases': [
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}
        tests27 = {'_class': '_empty',
                   'suites': [
                    {'cases': [
                        {'className': 'class271', 'duration': 11.1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class272', 'duration': 5.1,
                         'name': 'test2', 'status': 'PASSED'}]}]}

        self.jenkins.send_request = Mock(side_effect=[response, tests1,
                                                      tests27])

        # Mock the --build command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=[])

        jobs = self.jenkins.get_tests(last_build=build_kwargs)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs['ansible'].name.value, 'ansible')
        self.assertEqual(jobs['ansible'].url.value, 'url1')
        self.assertEqual(jobs['ansible-two'].name.value, 'ansible-two')
        self.assertEqual(jobs['ansible-two'].url.value, 'url2')

        builds_found1 = jobs['ansible'].builds.value
        self.assertEqual(len(builds_found1), 1)
        self.assertEqual(builds_found1['1'].build_id.value, '1')
        self.assertEqual(builds_found1['1'].status.value, 'SUCCESS')
        builds_found2 = jobs['ansible-two'].builds.value
        self.assertEqual(len(builds_found2), 1)
        self.assertEqual(builds_found2['27'].build_id.value, '27')
        self.assertEqual(builds_found2['27'].status.value, 'SUCCESS')

        tests_found1 = jobs['ansible'].builds.value['1'].tests
        self.assertEqual(len(tests_found1), 3)
        self.assertEqual(tests_found1['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found1['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found1['test1'].duration.value, 1000)
        self.assertEqual(tests_found1['test2'].result.value, 'SKIPPED')
        self.assertEqual(tests_found1['test2'].class_name.value, 'class2')
        self.assertEqual(tests_found1['test2'].duration.value, 0)
        self.assertEqual(tests_found1['test3'].result.value, 'FAILED')
        self.assertEqual(tests_found1['test3'].class_name.value, 'class2')
        self.assertEqual(tests_found1['test3'].duration.value, 2400)
        tests_found27 = jobs['ansible-two'].builds.value['27'].tests
        self.assertEqual(len(tests_found27), 2)
        self.assertEqual(tests_found27['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found27['test1'].class_name.value, 'class271')
        self.assertEqual(tests_found27['test1'].duration.value, 11100)
        self.assertEqual(tests_found27['test2'].result.value, 'PASSED')
        self.assertEqual(tests_found27['test2'].class_name.value, 'class272')
        self.assertEqual(tests_found27['test2'].duration.value, 5100)

    def test_get_tests_child(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when tests are located inside `childReports`.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1',
                              'lastBuild': {
                                  'number': 1, 'result': 'UNSTABLE',
                                  'duration': 3.5
                              }}]}
        tests = {'_class': '_empty',
                 'childReports': [
                     {
                         'result': {
                             'suites': [
                                {
                                    'cases': [
                                        {'className': 'class1',
                                         'duration': 1, 'name': 'test1',
                                         'status': 'PASSED'},
                                        {'className': 'class2',
                                         'duration': 0, 'name': 'test2',
                                         'status': 'SKIPPED'},
                                        {'className': 'class2',
                                         'duration': 2.4, 'name': 'test3',
                                         'status': 'FAILED'},
                                        {'className': 'class2',
                                         'duration': 120.0, 'name': 'test4',
                                         'status': 'REGRESSION'}
                                    ]
                                }
                             ]
                         }
                     }
                 ]}

        self.jenkins.send_request = Mock(side_effect=[response, tests])

        # Mock the --build command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=[])

        jobs = self.jenkins.get_tests(last_build=build_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'UNSTABLE')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 4)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1000)
        self.assertEqual(tests_found['test2'].result.value, 'SKIPPED')
        self.assertEqual(tests_found['test2'].class_name.value, 'class2')
        self.assertEqual(tests_found['test2'].duration.value, 0)
        self.assertEqual(tests_found['test3'].result.value, 'FAILED')
        self.assertEqual(tests_found['test3'].class_name.value, 'class2')
        self.assertEqual(tests_found['test3'].duration.value, 2400)
        self.assertEqual(tests_found['test4'].result.value, 'REGRESSION')
        self.assertEqual(tests_found['test4'].class_name.value, 'class2')
        self.assertEqual(tests_found['test4'].duration.value, 120000)

    def test_get_tests_filter_tests(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when filtering using --tests argument.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['test1',
                                                              'test3'])

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 2)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1000)
        self.assertEqual(tests_found['test3'].result.value, 'FAILED')
        self.assertEqual(tests_found['test3'].class_name.value, 'class2')
        self.assertEqual(tests_found['test3'].duration.value, 2400)

    def test_get_tests_filter_test_duration(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when filtering using --test-duration argument.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        test_duration = Argument("test_duration", arg_type=str, description="",
                                 value=[">=1", "<3"], ranged=True)

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs,
                                      test_duration=test_duration)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 2)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1000)
        self.assertEqual(tests_found['test3'].result.value, 'FAILED')

    def test_get_tests_filter_test_result(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when filtering using --test-result argument.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['passed',
                                                              'FailED'])

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs,
                                      test_result=tests_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')

        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')

        tests_found = job.builds.value['1'].tests
        self.assertEqual(len(tests_found), 2)
        self.assertEqual(tests_found['test1'].result.value, 'PASSED')
        self.assertEqual(tests_found['test1'].class_name.value, 'class1')
        self.assertEqual(tests_found['test1'].duration.value, 1000)
        self.assertEqual(tests_found['test3'].result.value, 'FAILED')

    def test_get_tests_filter_tests_results_duration(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct when filtering using --tests, --test-result,
            --test-duration argument.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'cases': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['test1',
                                                              'test3'])
        test_duration = Argument("test_duration", arg_type=str, description="",
                                 value=["<3", ">1.5"], ranged=True)
        tests_result = MagicMock()
        type(tests_result).value = PropertyMock(return_value=['PASSED'])

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs,
                                      test_duration=test_duration,
                                      test_result=tests_result)
        self.assertEqual(len(jobs), 0)

    def test_get_tests_detect_failed_build(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests`
            properly handles the cases where the input is wrong or tests can't
            be requested.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'failure'}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['test1',
                                                              'test3'])

        self.jenkins.send_request = Mock(side_effect=[response, builds])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(self.jenkins.send_request.call_count, 2)
        self.assertEqual(len(jobs), 0)

    def test_get_tests_detect_test_404(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests`
            properly handles the cases where the input is wrong or tests can't
            be requested.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['test1',
                                                              'test3'])

        self.jenkins.send_request = Mock(side_effect=[response, builds,
                                                      JenkinsError("404")])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(self.jenkins.send_request.call_count, 3)
        self.assertEqual(len(jobs), 0)

    def test_get_tests_raise_test_exception(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests`
            properly handles the cases where there is an exception querying for
            tests.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=['test1',
                                                              'test3'])

        self.jenkins.send_request = Mock(side_effect=[response, builds,
                                                      JenkinsError("error")])

        with self.assertRaises(JenkinsError):
            self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(self.jenkins.send_request.call_count, 3)

    def test_get_tests_no_test_suites(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct and detects when the API response for tests does not
            contain any tests.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty'}

        # Mock the --builds command line argument
        build_kwargs = Mock(spec=Argument)
        build_kwargs.value = ['1']
        tests_kwargs = Mock(spec=Argument)
        tests_kwargs.value = []

        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')
        self.assertEqual(self.jenkins.send_request.call_count, 3)

    def test_get_tests_no_cases(self):
        """
            Tests that the internal logic from :meth:`Jenkins.get_tests` is
            correct and detects cases where the API response contains a test
            suite, but no test cases inside.
        """

        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': 'ansible', 'url': 'url1'}]}

        builds = {'_class': '_empty',
                  'allBuilds': [{'number': 1, 'result': 'SUCCESS'},
                                {'number': 2, 'result': 'SUCCESS'}]}

        tests = {'_class': '_empty',
                 'suites': [
                    {'wrong_keyword': [
                        {'className': '', 'name': 'setUpClass (class1)'},
                        {'className': 'class1', 'duration': 1,
                         'name': 'test1', 'status': 'PASSED'},
                        {'className': 'class2', 'duration': 0,
                         'name': 'test2', 'status': 'SKIPPED'},
                        {'className': 'class2', 'duration': 2.4,
                         'name': 'test3', 'status': 'FAILED'}]}]}

        # Mock the --builds command line argument
        build_kwargs = MagicMock()
        type(build_kwargs).value = PropertyMock(return_value=['1'])
        tests_kwargs = MagicMock()
        type(tests_kwargs).value = PropertyMock(return_value=[])
        self.jenkins.send_request = Mock(side_effect=[response, builds, tests])

        jobs = self.jenkins.get_tests(builds=build_kwargs, tests=tests_kwargs)
        self.assertEqual(len(jobs), 1)
        job = jobs['ansible']
        self.assertEqual(job.name.value, 'ansible')
        self.assertEqual(job.url.value, 'url1')
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        self.assertEqual(builds_found['1'].build_id.value, '1')
        self.assertEqual(builds_found['1'].status.value, 'SUCCESS')
        self.assertEqual(self.jenkins.send_request.call_count, 3)

    def test_get_tests_no_builds_info(self):
        """Test that calling get_test without build information raises an
        exception."""
        self.assertRaises(MissingArgument, self.jenkins.get_tests)

    def test_get_tests_no_builds_info_general_exception(self):
        """Test that calling get_test without build informantion raises an
        exception."""
        self.assertRaises(SourceException, self.jenkins.get_tests)

    @patch("requests.get")
    def test_send_request(self, patched_get):
        """
            Test that send_request method parses the response correctly.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        patched_get.return_value = Mock(text=json.dumps(response))
        self.assertEqual(response, self.jenkins.send_request("test"))
        patched_get.assert_called_with(
            f'://{self.jenkins.username}:{self.jenkins.token}@/api/jsontest',
            verify=self.jenkins.cert, timeout=None
        )

    @patch("requests.get")
    def test_send_request_with_item(self, patched_get):
        """
            Test that send_request method parses the response correctly.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        patched_get.return_value = Mock(text=json.dumps(response))
        self.assertEqual(response, self.jenkins.send_request("test",
                                                             item="item"))
        api_part = "item/api/jsontest"
        patched_get.assert_called_with(
            f'://{self.jenkins.username}:{self.jenkins.token}@/{api_part}',
            verify=self.jenkins.cert, timeout=None
        )

    @patch("requests.get")
    def test_send_request_with_raw_response(self, patched_get):
        """
            Test that send_request returns the raw response.
        """
        response = {'jobs': [{'_class': 'org..job.WorkflowRun',
                              'name': "ansible", 'url': 'url1'}]}
        response = json.dumps(response)
        patched_get.return_value = Mock(text=response)
        self.assertEqual(response,
                         self.jenkins.send_request("test", raw_response=True))

        api_part = "api/jsontest"
        patched_get.assert_called_with(
            f'://{self.jenkins.username}:{self.jenkins.token}@/{api_part}',
            verify=self.jenkins.cert, timeout=None
        )


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

    def test_filter_jobs_scope(self):
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
        jobs_filtered = filter_jobs(response, jobs_scope="ans")
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'org..job.WorkflowRun',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}},
                    ]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_jobs_class(self):
        """
            Test that filter_jobs filters the jobs given the job _class.
        """
        response = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'jenkins.branch.OrganizationFolder',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'com.cloudbees.hudson.plugins.folder.Folder',
                     'name': "test_jobs", 'url': 'url2',
                     'lastBuild': {'number': 2, 'result': "FAILURE"}},
                    {'_class': 'hudson.model.FreeStyleProject',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}}]
        jobs_filtered = filter_jobs(response)
        expected = [{'_class': 'org..job.WorkflowRun',
                     'name': "ansible", 'url': 'url1',
                     'lastBuild': {'number': 1, 'result': "SUCCESS"}},
                    {'_class': 'hudson.model.FreeStyleProject',
                     'name': "ans2", 'url': 'url3',
                     'lastBuild': {'number': 0, 'result': "FAILURE"}},
                    ]
        self.assertEqual(jobs_filtered, expected)

    def test_filter_builds_builds_build_id_build_status(self):
        """Test that filter builds filters the builds given the user input."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': 'FAILURE'},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        builds = Mock()
        builds.value = ["3"]
        build_status = Mock()
        build_status.value = ["success"]
        checks = get_build_filters(builds=builds, build_status=build_status)
        builds_filtered = filter_builds(response, checks)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'}]
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
        checks = get_build_filters(builds=builds, build_status=build_status)
        builds_filtered = filter_builds(response, checks)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
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
        builds.value = ["3", "5"]
        checks = get_build_filters(builds=builds)
        builds_filtered = filter_builds(response, checks)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
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
        checks = get_build_filters(build_status=build_status)
        builds_filtered = filter_builds(response, checks)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
        self.assertEqual(builds_filtered, expected)

    def test_filter_builds_build_status_running_build(self):
        """Test that filter builds filters the builds given the user input.
        This tests simulates the case when a build is running, which sets the
        result field to None."""
        response = [{'_class': 'org..job.WorkflowRun', 'number': 3,
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': 4,
                     'result': None},
                    {'_class': 'org..job.WorkflowRun', 'number': 5,
                     'result': 'success'}]
        build_status = Mock()
        build_status.value = ["success"]
        checks = get_build_filters(build_status=build_status)
        builds_filtered = filter_builds(response, checks)
        expected = [{'_class': 'org..job.WorkflowRun', 'number': "3",
                     'result': 'SUCCESS'},
                    {'_class': 'org..job.WorkflowRun', 'number': "5",
                     'result': 'success'}]
        self.assertEqual(builds_filtered, expected)
