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

from unittest.mock import Mock, patch

from cibyl.exceptions.source import InvalidArgument
from cibyl.sources.elasticsearch.api import ElasticSearch
from tests.cibyl.utils import OpenstackPluginWithJobSystem


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
                                    'test_setup': 'rpm',
                                    'ip_version': 'ipv4',
                                    'test_suites': 'designate,neutron,octavia',
                                    'overcloud_templates':
                                        'designate,neutron,none'
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
                'key': 'test2',
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

        ip_address_kwargs = Mock()
        ip_address_kwargs.value = []

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          ip_version=ip_address_kwargs)
        deployment = jobs['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')

    def test_spec_deployment(self: object):
        self.es_api.get_jobs = Mock(side_effect=self.job_hits)
        spec = Mock()
        spec.value = []

        with self.assertRaises(InvalidArgument):
            self.es_api.get_deployment(spec=spec)

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_deployment_filtering(self: object,
                                  mock_query_hits: object) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment`
            is correct.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        # We need to mock the Argument kwargs passed. In this case
        # ip_address
        ip_address_kwargs = Mock()
        ip_address_kwargs.value = ['4']

        builds = self.es_api.get_deployment(jobs=jobs_argument,
                                            ip_version=ip_address_kwargs)

        deployment = builds['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment_filter_test_setup(self, mock_query_hits) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct and filters correctly
        by test setup value.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test']

        test_setup = Mock()
        test_setup.value = ["rpm"]

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          test_setup=test_setup)
        self.assertEqual(len(jobs), 1)
        deployment = jobs['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')
        test_collection = deployment.test_collection.value
        self.assertEqual(test_collection.setup.value, 'rpm')

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment_test_suites(self, mock_query_hits) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct and reads correctly
        the test suites value.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test$']

        spec = Mock()
        spec.value = []

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          spec=spec)
        self.assertEqual(len(jobs), 1)
        deployment = jobs['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')
        test_collection = deployment.test_collection.value
        self.assertEqual(test_collection.setup.value, 'rpm')
        suites = test_collection.tests.value
        self.assertEqual(suites, set(["neutron", "designate", "octavia"]))

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment_overcloud_templates(self, mock_query_hits) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct and reads correctly
        the overcloud_templates value.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test$']

        oc_templates = Mock()
        oc_templates.value = []

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          overcloud_templates=oc_templates)
        self.assertEqual(len(jobs), 1)
        deployment = jobs['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')
        overcloud_templates = deployment.overcloud_templates.value
        self.assertEqual(overcloud_templates, set(["neutron", "designate"]))

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment_oc_templates_filter(self, mock_query_hits) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct and reads correctly
        the overcloud_templates value and filters the jobs accordingly.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test$']

        oc_templates = Mock()
        oc_templates.value = ['octavia', 'nova']

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          overcloud_templates=oc_templates)
        self.assertEqual(len(jobs), 0)

    @patch.object(ElasticSearch, '_ElasticSearch__query_get_hits')
    def test_get_deployment_oc_templates_filter_found(self,
                                                      mock_query_hits) -> None:
        """Tests that the internal logic from
        :meth:`ElasticSearch.get_deployment` is correct and reads correctly
        the overcloud_templates value and filters the jobs accordingly.
        """
        mock_query_hits.return_value = self.tests_hits

        jobs_argument = Mock()
        jobs_argument.value = ['test$']

        oc_templates = Mock()
        oc_templates.value = ['neutron', 'nova']

        jobs = self.es_api.get_deployment(jobs=jobs_argument,
                                          overcloud_templates=oc_templates)
        self.assertEqual(len(jobs), 1)
        deployment = jobs['test'].deployment.value
        network = deployment.network.value
        self.assertEqual(network.ip_version.value, '4')
        self.assertEqual(deployment.topology.value, '')
        overcloud_templates = deployment.overcloud_templates.value
        self.assertEqual(overcloud_templates, set(["neutron", "designate"]))
