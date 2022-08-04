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
import sys

from cibyl.cli.main import main
from tests.cibyl.e2e.containers.elasticsearch import ElasticSearchContainer
from tests.cibyl.e2e.fixtures import EndToEndTest


class TestElasticSearch(EndToEndTest):
    """Tests queries regarding the ElasticSearch source.
    """

    def test_jobs(self):
        """Checks that jobs are retrieved with the "--jobs" flag.
        """
        with ElasticSearchContainer(index_name='logstash_jenkins_jobs'):
            sys.argv = [
                'cibyl',
                '--config', 'tests/cibyl/e2e/data/configs/elasticsearch.yaml',
                '-f', 'text',
                '-vv', 'query',
                '--jobs'
            ]

            main()

            self.assertIn('Total jobs found in query: 0', self.stdout)
