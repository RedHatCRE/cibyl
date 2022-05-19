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
from cibyl.utils.strings import IndentedTextBuilder
from tests.e2e.containers.zuul import OpenDevZuulContainer
from tests.e2e.fixtures import EndToEndTest


class TestQueryLevel(EndToEndTest):
    """Tests all the different options available for each of the query
    levels available on a zuul source. For example: fetching all jobs,
    fetching jobs by URL, by name...
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
            '--tenants', '^(example-tenant)$'
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
            '--tenants', '^(example-tenant)$',
            '--projects'
        ]

        main()

        self.assertIn(
            "Total projects found in query for tenant 'example-tenant': 3",
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
            '--tenants', '^(example-tenant)$',
            '--projects', 'test1'
        ]

        main()

        self.assertIn(
            "Project: test1",
            self.output
        )

        self.assertIn(
            "Total projects found in query for tenant 'example-tenant': 1",
            self.output
        )

    def test_get_project_url(self):
        """Checks that "-v" will print a project's URL.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants', '^(example-tenant)$',
            '--projects', 'test1',
            '-v'
        ]

        main()

        self.assertIn(
            "Project: test1",
            self.output
        )

        self.assertIn(
            "URL: http://localhost:9000/t/example-tenant/project/test1",
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
            '--tenants', '^(example-tenant)$',
            '--jobs'
        ]

        main()

        self.assertIn(
            "Total jobs found in query for tenant 'example-tenant': 65",
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
            '--tenants', '^(example-tenant)$',
            '--jobs', 'build-docker-image'
        ]

        main()

        self.assertIn(
            "Job: build-docker-image",
            self.output
        )

        self.assertIn(
            "Total jobs found in query for tenant 'example-tenant': 1",
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
            '--tenants', '^(example-tenant)$',
            '--jobs', '--job-url',
            'http://localhost:9000/t/example-tenant/job/build-docker-image'
        ]

        main()

        self.assertIn(
            'Job: build-docker-image',
            self.output
        )

        self.assertIn(
            "Total jobs found in query for tenant 'example-tenant': 1",
            self.output
        )

    def test_get_job_url(self):
        """Checks that "-v" will print a job's URL.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants', '^(example-tenant)$',
            '--jobs', 'build-docker-image',
            '-v'
        ]

        main()

        self.assertIn(
            "Job: build-docker-image",
            self.output
        )

        self.assertIn(
            "URL: "
            "http://localhost:9000/t/example-tenant/job/build-docker-image",
            self.output
        )

    def test_get_job_variants(self):
        """Checks retrieved variants by "--jobs --variants" flag.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants', '^(example-tenant)$',
            '--jobs', 'build-docker-image',
            '--variants'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Environment: env_1', 0)
        expected.add('System: zuul_system', 1)
        expected.add('Tenant: example-tenant', 2)
        expected.add('Projects: ', 3)
        expected.add('No projects found in query.', 4)
        expected.add('Jobs: ', 3)
        expected.add('Job: build-docker-image', 4)
        expected.add('Variants: ', 5)
        expected.add('Variant: ', 6)
        expected.add('Description: Build a docker image.', 7)

        self.assertIn(
            expected.build(),
            self.output
        )


class TestQueryComposing(EndToEndTest):
    """Tests that multiple queries on the same request end with an output
    that combines the result of all them. For example: 'cibyl
    --tenants --projects projectA' will fetch all tenants and get
    information on only the 'projectA' project.
    """
    zuul = OpenDevZuulContainer()

    @classmethod
    def setUpClass(cls):
        cls.zuul.start()

    @classmethod
    def tearDownClass(cls):
        cls.zuul.stop()

    def test_tenants_with_project(self):
        """Checks that '--tenants --project projectA' gets you all tenants
        as well."""
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants',
            '--projects', '^test2$'
        ]

        main()

        expected1 = IndentedTextBuilder()
        expected1.add('Tenant: example-tenant', 2)

        expected2 = IndentedTextBuilder()
        expected2.add('Tenant: example-tenant-2', 2)
        expected2.add('Projects: ', 3)
        expected2.add('Project: test2', 4)

        self.assertIn(expected1.build(), self.output)
        self.assertIn(expected2.build(), self.output)

    def test_tenants_with_jobs(self):
        """Checks that '--tenants --project projectA' gets you all tenants
        as well."""
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants',
            '--jobs', '^build-docker-image$'
        ]

        main()

        expected1 = IndentedTextBuilder()
        expected1.add('Environment: env_1', 0)
        expected1.add('System: zuul_system', 1)
        expected1.add('Tenant: example-tenant', 2)
        expected1.add('Projects: ', 3)
        expected1.add('No projects found in query.', 4)
        expected1.add('Jobs: ', 3)
        expected1.add('Job: build-docker-image', 4)

        expected2 = IndentedTextBuilder()
        expected2.add('Tenant: example-tenant-2', 2)

        self.assertIn(expected1.build(), self.output)
        self.assertIn(expected2.build(), self.output)

    def test_projects_with_jobs(self):
        """Checks that '--tenants --project projectA' gets you all tenants
        as well."""
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--projects', '^test2$',
            '--jobs', '^build-docker-image$'
        ]

        main()

        expected1 = IndentedTextBuilder()
        expected1.add('Tenant: example-tenant-2', 2)
        expected1.add('Projects: ', 3)
        expected1.add('Project: test2', 4)

        expected2 = IndentedTextBuilder()
        expected2.add('Tenant: example-tenant', 2)
        expected2.add('Projects: ', 3)
        expected2.add('No projects found in query.', 4)
        expected2.add('Jobs: ', 3)
        expected2.add('Job: build-docker-image', 4)

        self.assertIn(expected1.build(), self.output)
        self.assertIn(expected2.build(), self.output)


class TestOutputFormatting(EndToEndTest):
    """Tests that verify specific conditions that shall be met on Cibyl's
    output.
    """
    zuul = OpenDevZuulContainer()

    @classmethod
    def setUpClass(cls):
        cls.zuul.start()

    @classmethod
    def tearDownClass(cls):
        cls.zuul.stop()

    def test_no_jobs_on_tenant_query(self):
        """Checks that no 'Jobs found in tenant...' string is printed for a
        '--tenants' query.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '-vv',
            '--tenants', '^(example-tenant)$'
        ]

        main()

        self.assertNotIn(
            "Total jobs found in query for tenant 'example-tenant':",
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
            '--tenants', '^(example-tenant)$',
            '--projects'
        ]

        main()

        self.assertNotIn(
            "Total jobs found in query for tenant 'example-tenant':",
            self.output
        )

    def test_no_tenants_message(self):
        """Checks that a 'no tenants found' message is printed when the
        query did not find any tenant.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants', '^(some-unknown-tenant)$',
        ]

        main()

        self.assertIn(
            'No tenants found in query.',
            self.output
        )

    def test_no_projects_message(self):
        """Checks that a 'no tenants found' message is printed when the
        query did not find any project.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants',
            '--project', '^(some-unknown-project)$'
        ]

        main()

        self.assertIn(
            'No projects found in query.',
            self.output
        )

    def test_no_jobs_message(self):
        """Checks that a 'no jobs found' message is printed when the
        query did not find any jobs.
        """
        sys.argv = [
            '',
            '--config', 'tests/e2e/data/configs/zuul.yaml',
            '-f', 'text',
            '--tenants',
            '--jobs', '^(some-unknown-job)$'
        ]

        main()

        self.assertIn(
            'No jobs found in query.',
            self.output
        )


class TestDefaults(EndToEndTest):
    """Tests for default query values extracted from the configuration
    file.
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

    def test_default_tenants_are_overridden(self):
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
