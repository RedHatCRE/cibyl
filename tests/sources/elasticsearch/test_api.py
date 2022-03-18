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
