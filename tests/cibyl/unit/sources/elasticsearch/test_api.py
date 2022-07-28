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
from __future__ import print_function

from unittest import TestCase
from unittest.mock import Mock, patch

from cibyl.cli.argument import Argument
from cibyl.exceptions.source import MissingArgument
from cibyl.sources.elasticsearch.api import ElasticSearch


class TestElasticSearch(TestCase):
    """Test cases for :class:`ElasticSearch`.
    """

    def setUp(self) -> None:
        self.es_api = ElasticSearch(elastic_client=Mock())
        self.job_hits = [
                    {
                        '_id': 1,
                        '_score': 1.0,
                        '_source': {
                            'job_name': 'test',
                            'job_url': 'http://domain.tld/test',

                        }
                    },
                    {
                        '_id': 2,
                        '_score': 1.0,
                        '_source': {
                            'job_name': 'test2',
                            'job_url': 'http://domain.tld/test2',
                        }
                    },
                    {
                        '_id': 3,
                        '_score': 1.0,
                        '_source': {
                            'job_name': 'test3',
                            'job_url': 'http://domain.tld/test3',
                        }
                    },
                    {
                        '_id': 4,
                        '_score': 1.0,
                        '_source': {
                            'job_name': 'test4',
                            'job_url': 'http://domain.tld/test4',
                        }
                    }
        ]

        self.build_hits = [
                    {
                        '_source': {
                            'job_name': 'test',
                            'job_url': 'http://domain.tld/test/',
                            'build_result': 'SUCCESS',
                            'build_id': '1',
                            'time_duration': 20,
                            'build_url': 'http://domain.tld/test/7',
                            'ip_version': 'ipv4',
                            'network_backend': 'local_area_n',
                            'test_name': 'it_is_just_a_test',
                            'test_time': '0.001',
                            'test_class_name': 'folder.file.ClassName'
                        }
                    },
                    {
                        '_source': {
                            'job_name': 'test2',
                            'job_url': 'http://domain.tld/test2/',
                            'build_result': 'FAIL',
                            'build_id': '2',
                            'time_duration': 10,
                            'build_url': 'http://domain.tld/test2/8',
                            'ip_version': 'ipv6',
                            'network_backend': 'local_area_n',
                            'test_name': 'it_is_just_a_test2',
                            'test_time': '0.0001_bad_parsed',
                        }
                    }
        ]

        self.tests_hits = [
            {
                '_source': {
                    'job_name': 'test',
                    'job_url': 'http://domain.tld/test/',
                    'build_result': 'SUCCESS',
                    'build_id': '1',
                    'build_num': '1',
                    'test_name': 'it_is_just_a_test',
                    'time_duration': '720',
                    'test_status': 'SUCCESS',
                    'test_time': '720',
                }
            },
            {
                '_source': {
                    'job_name': 'test2',
                    'job_url': 'http://domain.tld/test2/',
                    'build_result': 'FAIL',
                    'build_id': '2',
                    'build_num': '2',
                    'test_name': 'it_is_just_a_test2',
                    'time_duration': '0.0001_bad_parsed',
                    'test_status': 'FAIL',
                    'test_time': '0.0001_bad_parsed',
                }
            }
        ]

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_jobs(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearch.get_jobs`
            is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)

        self.assertEqual(len(jobs), 4)
        self.assertTrue('test' in jobs)
        self.assertEqual(jobs['test'].name.value, 'test')
        self.assertEqual(jobs['test'].url.value, "http://domain.tld/test")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_jobs_filter(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearch.get_jobs`
            is correct and regex filtering works correctly.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['4$']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)

        self.assertEqual(len(jobs), 1)
        self.assertTrue('test4' in jobs)
        self.assertEqual(jobs['test4'].name.value, 'test4')
        self.assertEqual(jobs['test4'].url.value, "http://domain.tld/test4")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_jobs_jobs_scope(self: object, mock_query_hits: object):
        """Tests that the internal logic from :meth:`ElasticSearch.get_jobs`
            is correct using jobs_scope argument.
        """
        mock_query_hits.return_value = self.job_hits

        jobs = self.es_api.get_jobs(jobs_scope='test4')

        self.assertEqual(len(jobs), 1)
        self.assertTrue('test4' in jobs)
        self.assertEqual(jobs['test4'].name.value, 'test4')
        self.assertEqual(jobs['test4'].url.value, "http://domain.tld/test4")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_builds(self, mock_query_hits) -> None:
        """Tests that the internal logic from
           :meth:`ElasticSearch.get_builds` is correct.
        """

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        mock_query_hits.return_value = self.build_hits

        jobs = self.es_api.get_builds(jobs=jobs_argument)
        builds = jobs['test'].builds
        self.assertEqual(len(jobs), 2)
        self.assertEqual(len(builds), 1)

        build = builds['1']
        self.assertEqual(build.build_id.value, '1')
        self.assertEqual(build.status.value, "SUCCESS")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_builds_by_status(self, mock_query_hits) -> None:
        """Tests filtering by status in :meth:`ElasticSearch.get_builds`
            is correct.
        """

        mock_query_hits.side_effect = [self.job_hits, self.build_hits]

        # We need to mock the Argument kwargs passed. In this case
        # build_status
        jobs_argument = Mock()
        jobs_argument.value = ['test']
        status_argument = Mock(spec=Argument)
        status_argument.value = ['fAiL']

        builds = self.es_api.get_builds(build_status=status_argument,
                                        jobs=jobs_argument)
        builds_values = builds['test2'].builds
        build = builds_values['2']
        self.assertEqual(build.build_id.value, '2')
        self.assertEqual(build.status.value, "FAIL")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_builds_filter_jobs_no_match(self,
                                             mock_query_hits) -> None:
        """Tests filtering by status in :meth:`ElasticSearch.get_builds`
            is correct and that if no jobs satisfy the criteria, no jobs are
            returned.
        """
        mock_query_hits.side_effect = [self.job_hits, self.build_hits]

        status_argument = Mock(spec=Argument)
        status_argument.value = ['non-existing']

        builds = self.es_api.get_builds(build_status=status_argument)
        self.assertEqual(len(builds), 0)

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_builds_with_last_build(self, mock_query_hits) -> None:
        """Tests that the internal logic from
           :meth:`ElasticSearch.get_builds` is correct.
        """
        mock_query_hits.side_effect = [self.job_hits, self.build_hits]

        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = []
        builds = self.es_api.get_builds(last_build=builds_kwargs)

        test_builds = builds['test'].builds
        self.assertEqual(len(test_builds), 1)

        build = test_builds['1']
        self.assertEqual(build.build_id.value, '1')
        self.assertEqual(build.status.value, "SUCCESS")

        test_builds = builds['test2'].builds
        self.assertEqual(len(test_builds), 1)

        build = test_builds['2']
        self.assertEqual(build.build_id.value, '2')
        self.assertEqual(build.status.value, "FAIL")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_last_build_filter_no_builds(self,
                                         mock_query_hits: object) -> None:
        """Tests that the internal logic from
           :meth:`ElasticSearch.get_builds` is correct and that if filtering by
           builds, no job is found to match the criteria, return no jobs.
        """
        mock_query_hits.side_effect = [self.job_hits, self.build_hits]

        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = []
        build_status_kwargs = Mock(spec=Argument)
        build_status_kwargs.value = []

        builds = self.es_api.get_builds(last_build=builds_kwargs,
                                        build_status=build_status_kwargs)
        self.assertEqual(0, len(builds))

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_tests(self, mock_query_hits) -> None:
        """Tests internal logic :meth:`ElasticSearch.get_tests`
            is correct.
        """
        mock_query_hits.return_value = self.tests_hits

        # We need to pass --builds or --last-build
        # to the get_tests method
        with self.assertRaises(MissingArgument):
            self.es_api.get_tests()

        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = []

        tests = self.es_api.get_tests(
            builds=builds_kwargs
        )

        self.assertTrue('it_is_just_a_test' in
                        tests['test'].builds['1'].tests)
        self.assertTrue(
            tests['test'].builds['1'].tests['it_is_just_a_test'].duration,
            1.000
        )

        # Test Filtering by test_result
        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = ['1', '2']

        test_result_kwargs = Mock(spec=Argument)
        test_result_kwargs.value = ['sucCess']

        tests = self.es_api.get_tests(
            builds=builds_kwargs,
            test_result=test_result_kwargs,
        )

        self.assertEqual(
            len(tests['test'].builds['1'].tests),
            1
        )
        self.assertTrue('it_is_just_a_test' in
                        tests['test'].builds['1'].tests)

        # Test Filtering by test_duration
        test_duration = Argument("test_duration", arg_type=str, description="",
                                 value=[">=600"], ranged=True)

        tests = self.es_api.get_tests(
            builds=builds_kwargs,
            test_duration=test_duration
        )

        self.assertEqual(
            len(tests['test'].builds['1'].tests),
            1
        )

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_tests_filter_by_tests_name(self, mock_query_hits) -> None:
        """Tests internal logic :meth:`ElasticSearch.get_tests`
            is correct and filters by test name supporting regex.
        """
        mock_query_hits.return_value = self.tests_hits

        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = []

        tests_kwargs = Mock(spec=Argument)
        tests_kwargs.value = ['test$']

        tests = self.es_api.get_tests(
            builds=builds_kwargs,
            tests=tests_kwargs
        )

        self.assertEqual(
            len(tests['test'].builds['1'].tests),
            1
        )

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_tests_jobs_filtered_no_tests(self, mock_query_hits) -> None:
        """Tests internal logic :meth:`ElasticSearch.get_tests`
            is correct and filters by test name supporting regex, if some jobs
            turn out to have no tests as a result of the filtering, they should
            not be returned.
        """
        mock_query_hits.return_value = self.tests_hits

        builds_kwargs = Mock(spec=Argument)
        builds_kwargs.value = ['']

        tests_kwargs = Mock(spec=Argument)
        tests_kwargs.value = ['test3$']

        tests = self.es_api.get_tests(
            builds=builds_kwargs,
            tests=tests_kwargs
        )

        self.assertEqual(len(tests), 0)

    @patch('cibyl.sources.elasticsearch.api.ElasticSearchClient')
    def test_setup(self, mock_client):
        """Test setup method of ElasticSearch"""
        es_api = ElasticSearch(elastic_client=None,
                               url="https://example.com:9200")
        client = mock_client.return_value
        client.connect.side_effect = None
        es_api.setup()
        mock_client.assert_called_with("https://example.com", 9200)

    @patch('cibyl.sources.elasticsearch.api.ElasticSearchClient')
    def test_ensure_teardown(self, mock_client):
        """Test setup method of ElasticSearch"""
        es_api = ElasticSearch(elastic_client=None,
                               url="https://example.com:9200")
        client = mock_client.return_value
        client.connect.side_effect = None
        es_api.ensure_source_setup()
        mock_client.assert_called_with("https://example.com", 9200)
        es_api.ensure_teardown()
        self.assertTrue(es_api.is_down())

    @patch('cibyl.sources.elasticsearch.api.ElasticSearchClient')
    def test_ensure_setup(self, mock_client):
        """Test ensure_setup method of ElasticSearch"""
        es_api = ElasticSearch(elastic_client=None,
                               url="https://example.com:9200")
        client = mock_client.return_value
        client.connect.side_effect = None
        es_api.ensure_source_setup()
        self.assertTrue(es_api.is_setup())
        mock_client.assert_called_with("https://example.com", 9200)
