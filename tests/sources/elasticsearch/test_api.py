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
from unittest.mock import Mock, patch

from cibyl.sources.elasticsearch.api import ElasticSearchOSP, QueryTemplate


class TestElasticsearchOSP(TestCase):
    """Test cases for :class:`ElasticSearchOSP`.
    """

    def setUp(self) -> None:
        self.es_api = ElasticSearchOSP(elastic_client=Mock())
        self.job_hit = [
            {
                '_index': 'test',
                '_id': 'random',
                '_score': 1.0,
                '_source': {
                    'jobName': 'test',
                    'envVars': {
                        'JOB_URL': 'http://domain.tld/test'
                    }
                }
            }
        ]
        self.build_hit = [
            {
                '_index': 'test',
                '_id': 'random',
                '_score': 1.0,
                '_source': {
                    'build_result': 'SUCCESS',
                    'build_id': '1',
                }
            }
        ]

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_jobs(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearchOSP.get_jobs`
            is correct.
        """
        mock_query_hits.return_value = self.job_hit

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)

        self.assertEqual(len(jobs), 1)
        self.assertTrue('test' in jobs)
        self.assertEqual(jobs['test'].name.value, 'test')
        self.assertEqual(jobs['test'].url.value, "http://domain.tld/test")

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_get_builds(self: object, mock_query_hits: object) -> None:
        """Tests that the internal logic from :meth:`ElasticSearchOSP.get_builds`
            is correct.
        """
        mock_query_hits.return_value = self.job_hit

        jobs_argument = Mock()
        jobs_argument.value = ['test']
        jobs = self.es_api.get_jobs(jobs=jobs_argument)
        self.assertEqual(len(jobs), 1)

        self.es_api.get_jobs = Mock()
        self.es_api.get_jobs.return_value = jobs
        mock_query_hits.return_value = self.build_hit

        builds = self.es_api.get_builds()['test'].builds
        self.assertEqual(len(builds), 1)

        build = builds['1']
        self.assertEqual(build.build_id.value, '1')
        self.assertEqual(build.status.value, "SUCCESS")


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

    def test_constructor(self: object) -> None:
        """Test :class:`QueryTemplate` exceptions and
           if it returns valid templates
        """
        with self.assertRaises(TypeError):
            QueryTemplate('search_key', 'search_value')

        # These are simple tests, but if we change something in
        # :class:`QueryTemplate` tests will fail
        self.assertEqual(QueryTemplate('search_key', []).get, '')
        self.assertEqual(
            QueryTemplate('search_key', ['test']).get,
            self.one_element_template
        )
        self.assertEqual(
            QueryTemplate('search_key', ['test', 'test2']).get,
            self.multiple_element_template
        )
