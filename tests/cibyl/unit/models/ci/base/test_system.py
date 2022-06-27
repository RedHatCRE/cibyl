"""
# Copyright 2022 Red Hat
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
# pylint: disable=no-member
import unittest

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.models.model import Model
from cibyl.models.product.feature import Feature


class TestSystem(unittest.TestCase):
    """Test the System class."""

    def setUp(self):
        self.name = "test"
        self.system_type = "test_type"
        self.system = System(self.name, self.system_type, Model)
        self.other_system = System(self.name, self.system_type, Model)

    def test_new_system_name(self):
        """Test the name attribute of the System class."""
        system = System("test", "test_type", Model)
        attribute_name = 'name'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"System lacks an attribute: {attribute_name}")
        self.assertEqual(system.name.value, "test")
        system_name = system.name.value
        self.assertEqual(system_name, "test",
                         msg=f"System should be test, not {system_name}")

    def test_new_system_type(self):
        """Test the type attribute of the System class."""
        system = System("test", "test_type", Model)
        attribute_name = 'system_type'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"System lacks an attribute: {attribute_name}")
        type_name = system.system_type.value
        msg_str = f"System type should be test_type, not {type_name}"
        self.assertEqual(type_name, "test_type", msg=msg_str)

    def test_export_attributes_to_source(self):
        """Test system export_attributes_to_source method."""
        output = self.system.export_attributes_to_source()
        self.assertEqual({}, output)

    def test_add_feature(self):
        self.system.add_feature(Feature("test", True))
        self.assertEqual(len(self.system.features), 1)
        feature = self.system.features["test"]
        self.assertEqual(feature.name.value, "test")
        self.assertEqual(feature.present.value, True)


class TestJobsSystem(unittest.TestCase):
    """Test the JobsSystem class."""

    def setUp(self):
        self.name = "test"
        self.system_type = "test_type"
        self.system = JobsSystem(self.name, self.system_type,
                                 jobs_scope="phase1")
        self.other_system = JobsSystem(self.name, self.system_type)

    def test_add_job(self):
        """Test adding a new job to a system."""
        job = Job("test_job")
        self.system.add_job(job)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value["test_job"])

    def test_system_populate(self):
        """Test adding a new job to a system."""
        job = Job("test_job")
        jobs = AttributeDictValue(name='jobs', value={'test_job': job},
                                  attr_type=Job)
        self.system.populate(jobs)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value["test_job"])

    def test_query_attribute(self):
        """Test system queried attribute."""
        self.assertFalse(self.system.is_queried())
        self.system.register_query()
        self.assertTrue(self.system.is_queried())

    def test_export_attributes_to_source(self):
        """Test system export_attributes_to_source method."""
        output = self.system.export_attributes_to_source()
        self.assertEqual(1, len(output))
        self.assertEqual(output['jobs_scope'], 'phase1')

    def test_system_jobs_constructor(self):
        jobs = {'test_job': Job("test_job")}
        system = JobsSystem("test", "test", jobs=jobs)
        self.assertEqual(1, len(system.jobs.value))
