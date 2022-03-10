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
from unittest.mock import Mock

from cibyl.sources.elasticsearch.api import ElasticSearchOSP


def return_hits():
    """It will return fake hits from elasticsearch
    to use it in a Mock
    """
    return [
        {
            '_index': 'test',
            '_id': 'random',
            '_score': 1.0
        }
    ]


class TestElasticsearchOSP(TestCase):
    """Test cases for :class:`ElasticSearchOSP`.
    """

    def setUp(self) -> None:
        self.es_api = ElasticSearchOSP(Mock())

    def test_return_list(self):
        """Tests if :meth:`ElasticSearchOSP.get_jobs_by_name`
        return a list.
        """
        self.es_api.get_jobs_by_name = Mock()
        self.es_api.get_jobs_by_name.side_effect = return_hits
        self.assertIsInstance(self.es_api.get_jobs_by_name(), list)
