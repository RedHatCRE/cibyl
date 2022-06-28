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

from cibyl.models.attribute import (AttributeDictValue, AttributeListValue,
                                    AttributeValue)
from cibyl.models.ci.zuul.job import Job


class TestJob(TestCase):
    """Tests for :class:`Job`.
    """

    def test_equality_by_type(self):
        """Checks that two jobs are different if they are of different type.
        """
        job = Job('job', 'url')
        other = Mock()

        self.assertNotEqual(other, job)

    def test_equality_by_reference(self):
        """Checks that a job is equal to itself.
        """
        job = Job('job', 'url')
        other = job

        self.assertEqual(other, job)

    def test_equality_by_contents(self):
        """Checks that two jobs are equal if they have the same data.
        """
        name = 'job'
        url = 'url'

        build = Mock()
        variant = Mock()

        job = Job(name, url)
        job.add_build(build)
        job.add_variant(variant)

        other = Job(name, url)
        other.add_build(build)
        other.add_variant(variant)

        self.assertEqual(other, job)

    def test_has_variants_attribute(self):
        """Checks that a 'variants' attribute is added to the object.
        """
        job = Job('name', 'url')

        self.assertIsInstance(job.variants, AttributeListValue)

    def test_add_variant(self):
        """Checks that some random variant can be added to the model.
        """
        variant = Mock()

        job = Job('name', 'url')
        job.add_variant(variant)

        self.assertIn(variant, job.variants)

    def test_add_variants_during_merge(self):
        """Checks that the job will copy the variants from another during
        merge.
        """
        variant = Mock()

        job1 = Job('name', 'url')
        job2 = Job('name', 'url')

        job2.add_variant(variant)
        job1.merge(job2)

        self.assertIn(variant, job1.variants)

    class TestVariant(TestCase):
        """Tests for :class:`Job.Variant`.
        """

        def test_attributes(self):
            """Checks that the variant has all its attributes.
            """
            variant = Job.Variant('parent')

            self.assertIsInstance(variant.parent, AttributeValue)
            self.assertIsInstance(variant.description, AttributeValue)
            self.assertIsInstance(variant.branches, AttributeListValue)
            self.assertIsInstance(variant.variables, AttributeDictValue)

        def test_equality_by_type(self):
            """Checks that two objects of different type are not equal.
            """
            variant = Job.Variant('parent')
            other = Mock()

            self.assertNotEqual(other, variant)

        def test_equality_by_reference(self):
            """Checks that two objects are equal if they are pointed by the same
            reference.
            """
            variant = Job.Variant('parent')
            other = variant

            self.assertEqual(other, variant)

        def test_equality_by_content(self):
            """Checks that two objects are equal if they have the same contents.
            """
            parent = 'parent'
            description = 'description'
            branches = ['branch1', 'branch2']
            variables = {'var1': 'val1'}

            variant1 = Job.Variant(parent, description, branches, variables)
            variant2 = Job.Variant(parent, description, branches, variables)

            self.assertEqual(variant2, variant1)
