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

from cibyl.outputs.cli.ci.system.impls.zuul.colored.trees.factory import \
    FlatTreeFactory


class TestFlatTreeFactory(TestCase):
    """Tests for :class:`FlatTreeFactory`.
    """

    def test_empty_jobs(self):
        """Checks what tree is produced when no job is given at the input.
        """
        jobs = []

        factory = FlatTreeFactory()

        root = factory.from_jobs(jobs)

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

        root = factory.from_jobs(jobs)

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(1, len(root.children))

        child = root.children[0]

        self.assertEqual(job1.name.value, child.name)
        self.assertEqual(job1, child.model)

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

        root = factory.from_jobs(jobs)

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.model)

        child2 = root.children[1]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.model)

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

        root = factory.from_jobs(jobs)

        self.assertEqual(FlatTreeFactory.ROOT_NAME, root.name)
        self.assertEqual(2, len(root.children))

        child1 = root.children[0]

        self.assertEqual(job1.name.value, child1.name)
        self.assertEqual(job1, child1.model)

        child2 = root.children[1]

        self.assertEqual(job2.name.value, child2.name)
        self.assertEqual(job2, child2.model)
