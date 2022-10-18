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

from cibyl.outputs.cli.ci.system.impls.zuul.colored.trees.factory import (
    FlatTreeFactory, HierarchicalTreeFactory)


class TestFlatTreeFactory(TestCase):
    """Tests for :class:`FlatTreeFactory`.
    """

    def test_empty_jobs(self):
        """Checks what tree is produced when no job is given at the input.
        """
        jobs = []

        factory = FlatTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(0, len(root.children))

    def test_single_job(self):
        """Checks what tree is produced when a single job is given at the
        input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'

        jobs = [
            job1
        ]

        factory = FlatTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(1, len(root.children))

        child = root.children[0]

        self.assertEqual(root, child.parent)
        self.assertEqual(job1.name.value, child.name)
        self.assertEqual(job1, child.value)
        self.assertEqual(0, len(child.children))

        # Check hierarchy
        self.assertEqual(root, child.parent)

    def test_multiple_independent_jobs(self):
        """Checks what tree is produced when multiple unrelated jobs are
        given at the input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'

        jobs = [
            job1,
            job2
        ]

        factory = FlatTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(0, len(child1.children))

        child2 = root.children[1]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(0, len(child2.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(root, child2.parent)

    def test_multiple_related_jobs(self):
        """Checks what tree is returned when multiple related jobs are
        given at the input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'
        job1.variants = []

        variant = Mock()
        variant.parent = Mock()
        variant.parent.value = job1.name.value

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'
        job2.variants = [
            variant
        ]

        jobs = [
            job1,
            job2
        ]

        factory = FlatTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(0, len(child1.children))

        child2 = root.children[1]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(0, len(child2.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(root, child2.parent)


class TestHierarchicalTreeFactory(TestCase):
    """Tests for :class:`HierarchicalTreeFactory`.
    """

    def test_empty_jobs(self):
        """Checks generated tree when no job is added at the input.
        """
        jobs = []

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(0, len(root.children))

    def test_single_job(self):
        """Checks generated tree when a single job is added at the input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'
        job1.variants = Mock()
        job1.variants.value = []

        jobs = [
            job1
        ]

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(1, len(root.children))

        child = root.children[0]

        self.assertEqual(job1.name.value, child.name)
        self.assertEqual(job1, child.value)
        self.assertEqual(0, len(child.children))

        # Check hierarchy
        self.assertEqual(root, child.parent)

    def test_multiple_independent_jobs(self):
        """Check generated tree when multiple unrelated jobs are added at
        the input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'
        job1.variants = Mock()
        job1.variants.value = []

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'
        job2.variants = Mock()
        job2.variants.value = []

        jobs = [
            job1,
            job2
        ]

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(0, len(child1.children))

        child2 = root.children[1]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(0, len(child2.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(root, child2.parent)

    def test_related_jobs(self):
        """Checks generated tree when related jobs are added at the input.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'

        job1.variants = Mock()
        job1.variants.value = []

        variant1 = Mock()
        variant1.parent = Mock()
        variant1.parent.value = job1.name.value
        variant1.name = Mock()
        variant1.name.value = 'variant1'

        job2.variants = Mock()
        job2.variants.value = [variant1]

        jobs = [
            job1,
            job2
        ]

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(1, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(1, len(child1.children))

        child2 = child1.children[0]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(0, len(child2.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(child1, child2.parent)

    def test_case_1(self):
        """Verifying a tree of three levels of depth.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'

        job3 = Mock()
        job3.name = Mock()
        job3.name.value = 'job3'

        job1.variants = Mock()
        job1.variants.value = []

        variant1 = Mock()
        variant1.parent = Mock()
        variant1.parent.value = job1.name.value
        variant1.name = Mock()
        variant1.name.value = 'variant1'

        job2.variants = Mock()
        job2.variants.value = [variant1]

        variant2 = Mock()
        variant2.parent = Mock()
        variant2.parent.value = job2.name.value
        variant2.name = Mock()
        variant2.name.value = 'variant2'

        job3.variants = Mock()
        job3.variants.value = [variant2]

        jobs = [
            job1,
            job2,
            job3
        ]

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(1, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(1, len(child1.children))

        child2 = child1.children[0]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(1, len(child2.children))

        child3 = child2.children[0]

        self.assertEqual(job3.name.value, child3.name)
        self.assertEqual(job3, child3.value)
        self.assertEqual(0, len(child3.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(child1, child2.parent)
        self.assertEqual(child2, child3.parent)

    def test_case_2(self):
        """Verifying a tree of three levels of depth with another branch at
        level 1.
        """
        job1 = Mock()
        job1.name = Mock()
        job1.name.value = 'job1'

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = 'job2'

        job3 = Mock()
        job3.name = Mock()
        job3.name.value = 'job3'

        job4 = Mock()
        job4.name = Mock()
        job4.name.value = 'job4'

        job1.variants = Mock()
        job1.variants.value = []

        variant1 = Mock()
        variant1.parent = Mock()
        variant1.parent.value = job1.name.value
        variant1.name = Mock()
        variant1.name.value = 'variant1'

        job2.variants = Mock()
        job2.variants.value = [variant1]

        variant2 = Mock()
        variant2.parent = Mock()
        variant2.parent.value = job2.name.value
        variant2.name = Mock()
        variant2.name.value = 'variant2'

        job3.variants = Mock()
        job3.variants.value = [variant2]

        job4.variants = Mock()
        job4.variants.value = []

        jobs = [
            job1,
            job2,
            job3,
            job4
        ]

        factory = HierarchicalTreeFactory()

        tree = factory.from_jobs(jobs)
        root = tree.root

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.value)
        self.assertEqual(1, len(child1.children))

        child2 = child1.children[0]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.value)
        self.assertEqual(1, len(child2.children))

        child3 = child2.children[0]

        self.assertEqual(job3.name.value, child3.name)
        self.assertEqual(job3, child3.value)
        self.assertEqual(0, len(child3.children))

        child4 = root.children[1]

        self.assertEqual(job4.name.value, child4.name)
        self.assertEqual(job4, child4.value)
        self.assertEqual(0, len(child4.children))

        # Check hierarchy
        self.assertEqual(root, child1.parent)
        self.assertEqual(child1, child2.parent)
        self.assertEqual(child2, child3.parent)
        self.assertEqual(root, child4.parent)
