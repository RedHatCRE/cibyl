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
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from cibyl.sources.elasticsearch.api import ElasticSearchOSP, QueryTemplate


class TestElasticsearchOSP(TestCase):
    """Test cases for :class:`ElasticSearchOSP`.
    """

    def setUp(self) -> None:
        self.es_api = ElasticSearchOSP(elastic_client=Mock())
        self.job_hits = [
                    {
                        '_id': 'random',
                        '_score': 1.0,
                        '_source': {
                            'jobName': 'test',
                            'envVars': {
                                'JOB_URL': 'http://domain.tld/test',
                                'JP_OSPD_PRODUCT_VERSION': '16',
                            }
                        }
                    },
                    {
                        '_id': 'random',
                        '_score': 1.0,
                        '_source': {
                            'jobName': 'test2',
                            'envVars': {
                                'JOB_URL': 'http://domain.tld/test2',
                                'JP_OSPD_PRODUCT_VERSION': '17.2',
                            }
                        }
                    },
                    {
                        '_id': 'random',
                        '_score': 1.0,
                        '_source': {
                            'jobName': 'test3',
                            'envVars': {
                                'JOB_URL': 'http://domain.tld/test3',
                                'JP_OSPD_PRODUCT_VERSION': '17.0',
                                'JP_OSPD_NETWORK_PROTOCOL': 'ipv4',
                            }
                        }
                    }
        ]

        self.build_hits = [
                    {
                        '_source': {
                            'buildResult': 'SUCCESS',
                            'buildID': '1',
                            'runDuration': 20
                        }
                    },
                    {
                        '_source': {
                            'buildResult': 'FAIL',
                            'buildID': '2',
                            'runDuration': 10
                        }
                    }
        ]

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_jobs(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearchOSP.get_jobs`
            is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)

        self.assertEqual(len(jobs), 3)
        self.assertTrue('test' in jobs)
        self.assertEqual(jobs['test'].name.value, 'test')
        self.assertEqual(jobs['test'].url.value, "http://domain.tld/test")

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_deployment(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearchOSP.get_deployment`
            is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        # We need to mock the Argument kwargs passed. In this case
        # ip_address
        ip_address_kwargs = MagicMock()
        ip_adress_value = PropertyMock(return_value=[])
        type(ip_address_kwargs).value = ip_adress_value

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          ip_version=ip_address_kwargs)
        deployment = jobs['test'].deployment.value
        self.assertEqual(deployment.release.value, '16')
        self.assertEqual(deployment.ip_version.value, 'unknown')
        self.assertEqual(deployment.topology.value, 'unknown')

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_deployment_filtering(self: object,
                                  mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearchOSP.get_jobs`
            is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        # We need to mock the Argument kwargs passed. In this case
        # ip_address
        ip_address_kwargs = MagicMock()
        ip_adress_value = PropertyMock(return_value=['4'])
        type(ip_address_kwargs).value = ip_adress_value

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          ip_version=ip_address_kwargs)
        deployment = jobs['test3'].deployment.value
        self.assertEqual(deployment.release.value, '17.0')
        self.assertEqual(deployment.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, 'unknown')

        release_kwargs = MagicMock()
        release_value = PropertyMock(return_value=['17.2'])
        type(release_kwargs).value = release_value

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          release=release_kwargs)
        deployment = jobs['test2'].deployment.value
        self.assertEqual(deployment.release.value, '17.2')
        self.assertEqual(deployment.ip_version.value, 'unknown')
        self.assertEqual(deployment.topology.value, 'unknown')

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_builds(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from
           :meth:`ElasticSearchOSP.get_builds` is correct.
        """
        mock_query_hits.return_value = self.job_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)
        self.assertEqual(len(jobs), 3)

        self.es_api.get_jobs = Mock()
        self.es_api.get_jobs.return_value = jobs
        mock_query_hits.return_value = self.build_hits

        builds = self.es_api.get_builds()['test'].builds
        self.assertEqual(len(builds), 2)

        build = builds['1']
        self.assertEqual(build.build_id.value, '1')
        self.assertEqual(build.status.value, "SUCCESS")

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_builds_by_status(self: object,
                                  mock_query_hits: object) -> None:
        """Tests filtering by status in :meth:`ElasticSearchOSP.get_builds`
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
