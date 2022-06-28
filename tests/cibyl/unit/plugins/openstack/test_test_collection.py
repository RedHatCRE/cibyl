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

from cibyl.plugins.openstack.test_collection import TestCollection


class TestOpenstackTestCollection(TestCase):
    """Test openstack TestCollection model."""
    def setUp(self):
        self.tests = set(["test1", "test2"])
        self.tests2 = set(["test4", "test3"])
        self.all_tests = self.tests.union(self.tests2)
        self.setup = 'rhos-release'
        self.collection = TestCollection(self.tests)
        self.collection2 = TestCollection(self.tests2, self.setup)

    def test_merge(self):
        """Test TestCollection merge method when both models have tests."""
        self.collection.merge(self.collection2)
        self.assertEqual(self.setup, self.collection.setup.value)
        self.assertEqual(self.all_tests, self.collection.tests.value)

    def test_merge_no_tests(self):
        """Test TestCollection merge method when only one model has tests."""
        other_collection = TestCollection()
        other_collection.merge(self.collection)
        self.assertIsNone(other_collection.setup.value)
        self.assertEqual(self.tests, other_collection.tests.value)
