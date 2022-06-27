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
import json

import requests
from overrides import overrides

from tests.cibyl.e2e.containers import ComposedContainer, wait_for


class ElasticSearchContainer(ComposedContainer):
    def __init__(self, **kwargs):
        super().__init__('tests/cibyl/e2e/data/images/elasticsearch')

        self._index_name = kwargs.get('index_name', 'logstash_jenkins_jobs')
        self._jenkins_mapping = kwargs.get(
            'jenkins_mapping',
            'tests/cibyl/e2e/data/images/elasticsearch/jenkins.mapping.json'
        )

    @property
    def url(self):
        # Defined on dockerfile
        return 'http://localhost:9200'

    @overrides
    def _wait_until_ready(self):
        wait_for(f'{self.url}')

    @overrides
    def _on_ready(self):
        # Prepare database
        with open(self._jenkins_mapping, 'r', encoding='utf-8') as mapping:
            # Create the index
            requests.put(
                f'{self.url}/{self._index_name}'
            )

            # It is a big mapping, increase the number of possible fields
            requests.put(
                f'{self.url}/{self._index_name}/_settings',
                json={
                    'index.mapping.total_fields.limit': 2000
                }
            )

            # Load the mapping
            requests.put(
                f'{self.url}/{self._index_name}/_mapping',
                json=json.load(mapping)
            )
