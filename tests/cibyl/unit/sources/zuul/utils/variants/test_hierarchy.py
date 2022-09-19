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

from cibyl.sources.zuul.utils.variants.hierarchy import (
    HierarchyBuilder, HierarchyCrawler, HierarchyCrawlerFactory, JobFinder,
    RecursiveVariableSearch, SearchError, VariantFinder)


class TestJobFinder(TestCase):
    """Tests for :class:`JobFinder`.
    """

    def test_job_within_tenant(self):
        """Checks that the finder is able to find a job inside a tenant.
        """
        name = 'job'

        job = Mock()
        job.name = name

        tenant = Mock()
        tenant.jobs = Mock()
        tenant.jobs.return_value = Mock()
        tenant.jobs.return_value.with_name = Mock()
        tenant.jobs.return_value.get = Mock()
        tenant.jobs.return_value.get.return_value = [job]

        finder = JobFinder()

        self.assertEqual(job, finder.find(name).within(tenant))

        tenant.jobs.return_value.with_name.assert_called_once_with(f'^{name}$')

    def test_no_job_within_tenant(self):
        """Checks that an error is thrown if the finder cannot find a job
        inside a tenant.
        """
        name = 'job'

        tenant = Mock()
        tenant.jobs = Mock()
        tenant.jobs.return_value = Mock()
        tenant.jobs.return_value.get = Mock()
        tenant.jobs.return_value.get.return_value = []

        finder = JobFinder()

        with self.assertRaises(SearchError):
            finder.find(name).within(tenant)

    def test_many_jobs_within_tenant(self):
        """Checks that an error is thrown if the finder finds many jobs for
        the given name inside the tenant.
        """
        name = 'job'

        job = Mock()
        job.name = name

        tenant = Mock()
        tenant.jobs = Mock()
        tenant.jobs.return_value = Mock()
        tenant.jobs.return_value.get = Mock()
        tenant.jobs.return_value.get.return_value = [job, job]

        finder = JobFinder()

        with self.assertRaises(SearchError):
            finder.find(job.name).within(tenant)


class TestVariantFinder(TestCase):
    """Tests for :class:`VariantFinder`.
    """

    def test_finds_parent_of_variant(self):
        """Checks that the finder is able to fetch the parent of a variant.
        """
        branch = 'branch'

        tenant = Mock()

        variant = Mock()
        variant.parent = 'parent'
        variant.branches = [branch]
        variant.job.tenant = tenant

        parent = Mock()
        parent.branches = [branch]

        job = Mock()
        job.variants = Mock()
        job.variants.return_value = Mock()
        job.variants.return_value.get = Mock()
        job.variants.return_value.get.return_value = [parent]

        jobs = Mock()
        jobs.find = Mock()
        jobs.find.return_value = Mock()
        jobs.find.return_value.within = Mock()
        jobs.find.return_value.within.return_value = job

        tools = Mock()
        tools.jobs = jobs

        finder = VariantFinder(tools=tools)

        self.assertEqual(parent, finder.find().parent_of(variant))

        jobs.find.assert_called_once_with(variant.parent)
        jobs.find.return_value.within.assert_called_once_with(tenant)

    def test_parent_of_variant_not_found(self):
        """Checks that an error is thrown if the parent of a variant is not
        found.
        """
        branch1 = 'branch1'
        branch2 = 'branch2'

        tenant = Mock()

        variant = Mock()
        variant.parent = 'parent'
        variant.branches = [branch2]
        variant.job.tenant = tenant

        parent = Mock()
        parent.branches = [branch1]

        job = Mock()
        job.variants = Mock()
        job.variants.return_value = Mock()
        job.variants.return_value.get = Mock()
        job.variants.return_value.get.return_value = [parent]

        jobs = Mock()
        jobs.find = Mock()
        jobs.find.return_value = Mock()
        jobs.find.return_value.within = Mock()
        jobs.find.return_value.within.return_value = job

        tools = Mock()
        tools.jobs = jobs

        finder = VariantFinder(tools=tools)

        with self.assertRaises(SearchError):
            finder.find().parent_of(variant)


class TestHierarchyCrawler(TestCase):
    """Tests for :class:`HierarchyCrawler`.
    """

    def test_can_crawl_up_to_base(self):
        """Checks that the crawler will iterate over all elements an stop at
        the base job.
        """

        def parent_of(vrnt):
            if vrnt == variant:
                return parent

            if vrnt == parent:
                return grandparent

            return None

        grandparent = Mock()
        parent = Mock()
        variant = Mock()

        finder = Mock()
        finder.find = Mock()
        finder.find.return_value = Mock()
        finder.find.return_value.parent_of = Mock()
        finder.find.return_value.parent_of.side_effect = parent_of

        tools = Mock()
        tools.variants = finder

        crawler = HierarchyCrawler(
            variant=variant,
            tools=tools
        )

        iterator = iter(crawler)

        self.assertEqual(variant, next(iterator))
        self.assertEqual(parent, next(iterator))
        self.assertEqual(grandparent, next(iterator))

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_stops_if_error_in_search(self):
        """Checks that if an error occurs while looking for the parent
        variant, the iteration stops prematurely.
        """

        def parent_of(vrnt):
            if vrnt == variant:
                return parent

            if vrnt == parent:
                raise SearchError

            return None

        parent = Mock()
        variant = Mock()

        finder = Mock()
        finder.find = Mock()
        finder.find.return_value = Mock()
        finder.find.return_value.parent_of = Mock()
        finder.find.return_value.parent_of.side_effect = parent_of

        tools = Mock()
        tools.variants = finder

        crawler = HierarchyCrawler(
            variant=variant,
            tools=tools
        )

        iterator = iter(crawler)

        self.assertEqual(variant, next(iterator))
        self.assertEqual(parent, next(iterator))

        with self.assertRaises(StopIteration):
            next(iterator)


class TestHierarchyCrawlerFactory(TestCase):
    """Tests for :class:`HierarchyCrawlerFactory`.
    """

    def test_from_variant(self):
        """Tests that the factory can build an instance from a variant.
        """
        variant = Mock()

        factory = HierarchyCrawlerFactory()

        result = factory.from_variant(variant)

        self.assertEqual(variant, result.variant)


class TestHierarchyBuilder(TestCase):
    """Tests for :class:`HierarchyBuilder`.
    """

    def test_from_variant(self):
        """Checks that it is able to generate the hierarchy starting from a
        random variant.
        """
        grandparent = Mock()
        parent = Mock()
        variant = Mock()

        crawler = Mock()
        crawler.__iter__ = Mock()
        crawler.__iter__.return_value = iter([variant, parent, grandparent])

        tools = Mock()
        tools.crawlers = Mock()
        tools.crawlers.from_variant = Mock()
        tools.crawlers.from_variant.return_value = crawler

        builder = HierarchyBuilder(
            tools=tools
        )

        self.assertEqual(
            [
                variant,
                parent,
                grandparent
            ],
            builder.from_variant(variant).build()
        )

        tools.crawlers.from_variant.assert_called_once_with(variant)


class TestRecursiveVariableSearch(TestCase):
    """Tests for :class:`RecursiveVariableSearch`.
    """

    def test_search(self):
        """Checks that it is able to build the variable map going down a
        variant's hierarchy.
        """

        grandparent = Mock()
        grandparent.variables = {
            'var1': 'val1'
        }

        parent = Mock()
        parent.variables = {
            'var2': 'val2'
        }

        variant = Mock()
        variant.variables = {
            'var2': 'val3'
        }

        sequence = [variant, parent, grandparent]

        hierarchy = Mock()
        hierarchy.from_variant = Mock()
        hierarchy.from_variant.return_value = Mock()
        hierarchy.from_variant.return_value.build = Mock()
        hierarchy.from_variant.return_value.build.return_value = sequence

        tools = Mock()
        tools.hierarchy = hierarchy

        search = RecursiveVariableSearch(
            variant=variant,
            tools=tools
        )

        self.assertEqual(
            {
                'var1': 'val1',
                'var2': 'val3'
            },
            search.search()
        )

        hierarchy.from_variant.assert_called_once_with(variant)
