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

from cibyl.plugins.openstack.storage import Storage


class TestOpenstackStorage(TestCase):
    """Test openstack storage model."""
    def setUp(self):
        self.cinder_backend = "swift"
        self.second_storage = Storage(cinder_backend=self.cinder_backend)
        self.storage = Storage()

    def test_merge_method(self):
        """Test merge method of Storage class."""
        self.assertIsNone(self.storage.cinder_backend.value)
        self.storage.merge(self.second_storage)

        self.assertEqual(self.cinder_backend,
                         self.storage.cinder_backend.value)
