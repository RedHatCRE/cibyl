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

from cibyl.exceptions.elasticsearch import ElasticSearchError
from cibyl.sources.elasticsearch.api import ElasticSearchOSP


class TestElasticsearchOSP(TestCase):
    """Test cases for :class:`ElasticSearchOSP`.
    """

    def setUp(self) -> None:
        self.es_api = ElasticSearchOSP(Mock())
        self.hits = [
            {
                '_index': 'test',
                '_id': 'random',
                '_score': 1.0
            }
        ]
        self.job_name = 'job-test'
        self.query_type = {
            'valid': 'regexp',
            'not_valid': 'example'
        }

    @patch.object(ElasticSearchOSP, '_ElasticSearchOSP__query_get_hits')
    def test_method_return_list(self: object, mock_query_hits: object) -> None:
        """Tests if :meth:`ElasticSearchOSP.get_jobs_by_name`
        return a list.
        """
        mock_query_hits.return_value = self.hits
        self.assertIsInstance(
            self.es_api.get_jobs_by_name(self.job_name),
            list
        )

    def test_type_query(self: object) -> None:
        """Tests if :meth:`ElasticSearchOSP.get_jobs_by_name`
        raise an exception when query_type is not in the
        :const:`ElasticSearchOSP.ALLOWED_QUERIES`
        """
        self.assertRaises(
            ElasticSearchError,
            self.es_api.get_jobs_by_name,
            self.job_name,
            self.query_type['not_valid']
        )
