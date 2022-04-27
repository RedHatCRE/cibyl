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
from tests.e2e.containers.zuul import OpenDevZuulContainer
from tests.e2e.fixtures import EndToEndTest


class TestZuul(EndToEndTest):
    """Tests queries regarding the Zuul source.
    """

    def test_get_tenants(self):
        """Checks that tenants are retrieved with the "--tenants" flag.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
                '--tenants'
            ]

            main()

            self.assertIn('Total tenants found in query: 1', self.output)

    def test_get_tenants_by_name(self):
        """Checks that tenants are retrieved with the "--tenants name" flag.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
                '--tenants', 'example-tenant'
            ]

            main()

            self.assertIn('Tenant: example-tenant', self.output)
            self.assertIn('Total tenants found in query: 1', self.output)

    def test_no_jobs_on_tenant_query(self):
        """Checks that no 'Jobs found in tenant...' string is printed for a
        '--tenants' query.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
            ]

            main()

            self.assertNotIn('Total jobs found in query:', self.output)

    def test_get_jobs(self):
        """Checks that jobs are retrieved with the "--jobs" flag.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
                '--jobs'
            ]

            main()

            self.assertIn('Total jobs found in query: 65', self.output)

    def test_get_jobs_by_name(self):
        """Checks retrieved jobs by "--jobs name" flag.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
                '--jobs', 'build-docker-image'
            ]

            main()

            self.assertIn('Job: build-docker-image', self.output)
            self.assertIn('Total jobs found in query: 1', self.output)

    def test_get_jobs_by_url(self):
        """Checks retrieved jobs by "--jobs --job-url url" flag.
        """
        with OpenDevZuulContainer():
            sys.argv = [
                '',
                '--config', 'tests/e2e/data/configs/zuul.yaml',
                '-f', 'text',
                '-vv',
                '--jobs',
                '--job-url',
                'http://localhost:9000/t/example-tenant/job/build-docker-image'
            ]

            main()

            self.assertIn('Job: build-docker-image', self.output)
            self.assertIn('Total jobs found in query: 1', self.output)
