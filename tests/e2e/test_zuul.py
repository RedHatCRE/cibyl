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

    zuul = OpenDevZuulContainer()

    @classmethod
    def setUpClass(cls):
        cls.zuul.start()

    @classmethod
    def tearDownClass(cls):
        cls.zuul.stop()

    def test_get_tenants(self):
        """Checks that tenants are retrieved with the "--tenants" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants'
        ]

        main()

        self.assertIn('Total tenants found in query: 2', self.output)

    def test_get_tenants_by_name(self):
        """Checks that tenants are retrieved with the "--tenants name" flag.
        """
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

    def test_get_projects(self):
        """Checks that projects are retrieved with the "--projects" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--projects'
        ]

        main()

        self.assertIn(
            "Total projects found in tenant 'example-tenant': 4",
            self.output
        )

    def test_get_projects_by_name(self):
        """Checks that projects are retrieved with the "--projects name1
        name2" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--projects', 'test1'
        ]

        main()

        self.assertIn(
            "Project: test1",
            self.output
        )

        self.assertIn(
            "Total projects found in tenant 'example-tenant': 1",
            self.output
        )

    def test_no_jobs_on_tenant_query(self):
        """Checks that no 'Jobs found in tenant...' string is printed for a
        '--tenants' query.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant'
        ]

        main()

        self.assertNotIn(
            "Total jobs found in tenant 'example-tenant':",
            self.output
        )

    def test_no_jobs_on_projects_query(self):
        """Checks that no 'Jobs found in tenant...' string is printed for a
        '--projects' query.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--projects'
        ]

        main()

        self.assertNotIn(
            "Total jobs found in tenant 'example-tenant':",
            self.output
        )

    def test_get_jobs(self):
        """Checks that jobs are retrieved with the "--jobs" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--jobs'
        ]

        main()

        self.assertIn(
            "Total jobs found in tenant 'example-tenant': 65",
            self.output
        )

    def test_get_jobs_by_name(self):
        """Checks retrieved jobs by "--jobs name" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--jobs', 'build-docker-image'
        ]

        main()

        self.assertIn(
            "Job: build-docker-image",
            self.output
        )

        self.assertIn(
            "Total jobs found in tenant 'example-tenant': 1",
            self.output
        )

    def test_get_jobs_by_url(self):
        """Checks retrieved jobs by "--jobs --job-url url" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', 'example-tenant',
            '--jobs', '--job-url',
            'http://localhost:9000/t/example-tenant/job/build-docker-image'
        ]

        main()

        self.assertIn(
            'Job: build-docker-image',
            self.output
        )

        self.assertIn(
            "Total jobs found in tenant 'example-tenant': 1",
            self.output
        )


class TestZuulConfig(EndToEndTest):
    """Tests related to how the configuration file affects the Zuul source.
    """

    zuul = OpenDevZuulContainer()

    @classmethod
    def setUpClass(cls):
        cls.zuul.start()

    @classmethod
    def tearDownClass(cls):
        cls.zuul.stop()

    def test_default_tenants(self):
        """Checks that the configuration file can define the default tenants
        to be consulted.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul/with-tenants.yaml',
            '-f', 'text',
            '-vv',
            '--jobs'
        ]

        main()

        self.assertIn('Tenant: example-tenant', self.output)
        self.assertNotIn('Tenant: example-tenant-2', self.output)
        self.assertIn('Total tenants found in query: 1', self.output)

    def test_default_tenants_are_overriden(self):
        """Checks that the '--tenants' argument overrides the default
        tenants define in the configuration file.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul/with-tenants.yaml',
            '-f', 'text',
            '-vv',
            '--tenants'
        ]

        main()

        self.assertIn('Tenant: example-tenant', self.output)
        self.assertIn('Tenant: example-tenant-2', self.output)
        self.assertIn('Total tenants found in query: 2', self.output)
