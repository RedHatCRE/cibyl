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
from tests.e2e.fixtures import ElasticSearchTest


class TestElasticSearch(ElasticSearchTest):
    """Tests queries regarding the ElasticSearch source.
    """

    def test_jobs(self):
        """Checks that jobs are retrieved with the "--jobs" flag.
        """
        sys.argv = [
            '',
            '--config',
            'tests/e2e/configs/elasticsearch.yaml',
            '--jobs',
            '-vv'
        ]

        main()

        self.assertIn('Total jobs: 0', self.output)
