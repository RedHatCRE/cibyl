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
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from cibyl.cli.argument import Argument
from cibyl.exceptions.source import MissingArgument
from cibyl.sources.elasticsearch.api import ElasticSearch, QueryTemplate
from tests.utils import OpenstackPluginWithJobSystem


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
    def test_get_builds(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from
           :meth:`ElasticSearch.get_builds` is correct.
        """
        mock_query_hits.return_value = self.build_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)
        self.assertEqual(len(jobs), 2)

        self.es_api.get_jobs = Mock()
        self.es_api.get_jobs.return_value = jobs
        mock_query_hits.return_value = self.build_hits

        builds = self.es_api.get_builds()['test'].builds
        self.assertEqual(len(builds), 2)

        build = builds['1']
        self.assertEqual(build.build_id.value, '1')
        self.assertEqual(build.status.value, "SUCCESS")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_builds_by_status(self: object,
                                  mock_query_hits: object) -> None:
        """Tests filtering by status in :meth:`ElasticSearch.get_builds`
            is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)
        self.es_api.get_jobs = Mock()
        self.es_api.get_jobs.return_value = jobs
        mock_query_hits.return_value = self.build_hits

        # We need to mock the Argument kwargs passed. In this case
        # build_status
        status_argument = MagicMock()
        build_status = PropertyMock(return_value=['fAiL'])
        type(status_argument).value = build_status

        builds = self.es_api.get_builds(build_status=status_argument)
        builds_values = builds['test'].builds
        build = builds_values['2']
        self.assertEqual(build.build_id.value, '2')
        self.assertEqual(build.status.value, "FAIL")

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_tests(self: object,
                       mock_query_hits: object) -> None:
        """Tests internal logic :meth:`ElasticSearch.get_tests`
            is correct.
        """
        mock_query_hits.return_value = self.tests_hits

        # We need to pass --builds or --last-build
        # to the get_tests method
        with self.assertRaises(MissingArgument):
            self.es_api.get_tests()

        #
        builds_kwargs = MagicMock()
        builds_value = PropertyMock(return_value=[])
        type(builds_kwargs).value = builds_value

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
        builds_kwargs = MagicMock()
        builds_value = PropertyMock(return_value=['1', '2'])
        type(builds_kwargs).value = builds_value

        test_result_kwargs = MagicMock()
        test_result_value = PropertyMock(return_value=['sucCess'])
        type(test_result_kwargs).value = test_result_value

        tests = self.es_api.get_tests(
            builds=builds_kwargs,
            test_result=test_result_kwargs,
        )

        self.assertEqual(
            len(tests['test'].builds['2'].tests),
            0
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

        self.assertEqual(
            len(tests['test'].builds['2'].tests),
            0
        )

    @patch('cibyl.sources.elasticsearch.api.ElasticSearchClient')
    def test_setup(self, mock_client):
        """Test setup method of ElasticSearch"""
        es_api = ElasticSearch(elastic_client=None,
                               url="https://example.com:9200")
        client = mock_client.return_value
        client.connect.side_effect = None
        es_api.setup()
        mock_client.assert_called_with("https://example.com", 9200)


class TestElasticSearchOpenstackPlugin(OpenstackPluginWithJobSystem):
    """Test cases for :class:`ElasticSearch` with openstack plugin."""

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

        # This is an aggregation + query results
        self.tests_hits = [
            {
                '_source': {
                    'job_name': 'test',
                    'job_url': 'http://domain.tld/test/'
                },
                'key': 'test',
                'last_build': {
                    'hits': {
                        'hits': [
                            {

                                '_source': {
                                    'job_name': 'test',
                                    'job_url': 'http://domain.tld/test/',
                                    'ip_version': 'ipv4',
                                }
                            }
                        ]
                    }
                }
            },
            {
                '_source': {
                    'job_name': 'test2',
                    'job_url': 'http://domain.tld/test2/'
                },
                'key': 'test',
                'last_build': {
                    'hits': {
                        'hits': [
                            {
                                '_source': {
                                    'job_name': 'test2',
                                    'job_url': 'http://domain.tld/test2/',
                                    'ip_version': 'ipv4',
                                }
                            }
                        ]
                    }
                }
            }
        ]

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        # We need to mock the Argument kwargs passed. In this case
        # ip_address
        ip_address_kwargs = MagicMock()
        ip_address_value = PropertyMock(return_value=[])
        type(ip_address_kwargs).value = ip_address_value

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          ip_version=ip_address_kwargs)
        deployment = jobs['test'].deployment.value
        self.assertEqual(deployment.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_deployment_filtering(self: object,
                                  mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearch.get_jobs`
            is correct.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        # We need to mock the Argument kwargs passed. In this case
        # ip_address
        ip_address_kwargs = MagicMock()
        ip_address_value = PropertyMock(return_value=['4'])
        type(ip_address_kwargs).value = ip_address_value

        builds = self.es_api.get_deployment(jobs=jobs_argument,
                                            ip_version=ip_address_kwargs)

        deployment = builds['test'].deployment.value
        self.assertEqual(deployment.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')


class TestQueryTemplate(TestCase):
    """Test cases for :class:`QueryTemplate`.
    """

    def setUp(self) -> None:
        self.one_element_template = {
            'query':
                {
                    'match_phrase_prefix':
                    {
                        'search_key': 'test'
                    }
                }
        }

        self.multiple_element_template = {
            'query':
                {
                    'bool':
                    {
                        'minimum_should_match': 1,
                        'should': [
                            {
                                'match_phrase':
                                    {
                                        'search_key': 'test'
                                    }
                            },
                            {
                                'match_phrase':
                                    {
                                        'search_key': 'test2'
                                    }
                            }
                        ]
                    }
                }
        }

        self.all_elements_template = {
            'query':
                {
                    'exists':
                    {
                        'field': 'search_key'
                    }
                }
        }

    def test_constructor(self: object) -> None:
        """Test :class:`QueryTemplate` exceptions and
           if it returns valid templates
        """
        with self.assertRaises(TypeError):
            QueryTemplate('search_key', 'search_value')

        # These are simple tests, but if we change something in
        # :class:`QueryTemplate` tests will fail
        self.assertEqual(QueryTemplate('search_key', []).get,
                         self.all_elements_template)
        self.assertEqual(
            QueryTemplate('search_key', ['test']).get,
            self.one_element_template
        )
        self.assertEqual(
            QueryTemplate('search_key', ['test', 'test2']).get,
            self.multiple_element_template
        )
