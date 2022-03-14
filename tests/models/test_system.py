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
from cibyl.models.ci.job import Job
from cibyl.models.ci.pipeline import Pipeline
from cibyl.models.ci.system import JenkinsSystem, System, ZuulSystem
from cibyl.sources.source import Source


class TestSystem(unittest.TestCase):
    """Testing the System class"""
    def setUp(self):
        self.name = "test"
        self.system_type = "test_type"
        self.system = System(self.name, self.system_type)
        self.other_system = System(self.name, self.system_type)

    def test_new_system_name(self):
        """Testing the name attribute of the System class"""
        system = System("test", "test_type")
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
        """Testing the type attribute of the System class"""
        system = System("test", "test_type")
        attribute_name = 'system_type'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"System lacks an attribute: {attribute_name}")
        type_name = system.system_type.value
        msg_str = f"System type should be test_type, not {type_name}"
        self.assertEqual(type_name, "test_type", msg=msg_str)

    def test_add_job(self):
        """Testing adding a new job to a system"""
        job = Job("test_job")
        self.system.add_job(job)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value[0])

    def test_system_populate(self):
        """Testing adding a new job to a system"""
        job = Job("test_job")
        jobs = AttributeDictValue(name='jobs', value={'test_job': job},
                                  attr_type=Job)
        self.system.populate(jobs)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value[0])


class TestZuulSystem(unittest.TestCase):
    """Testing the ZuulSystem class"""
    def setUp(self):
        self.name = "test"
        self.system = ZuulSystem(self.name)
        self.other_system = ZuulSystem(self.name)

    def test_new_system_name(self):
        """Testing the type attribute of the ZuulSystem class"""
        self.assertTrue(
            hasattr(self.system, 'name'), msg="System lacks name attribute")
        system_name = self.system.name.value
        error_msg = f"System name should be {self.name}, not {system_name}"
        self.assertEqual(self.system.name.value, self.name,
                         msg=error_msg)

    def test_new_system_type(self):
        """Testing the type attribute of the ZuulSystem class"""
        self.assertTrue(
            hasattr(self.system, 'system_type'),
            msg="System lacks type attribute")
        system_type = self.system.system_type.value
        error_msg = f"System type should be zuul, not {system_type}"
        self.assertEqual(self.system.name.value, self.name,
                         msg=error_msg)

    def test_system_comparison(self):
        """Testing new ZuulSystem instances comparison"""
        self.assertEqual(
            self.system, self.other_system,
            msg="Systems {self.system.name.value} and \
{self.system.name.value} are not equal")

    def test_system_comparison_other_types(self):
        """Testing new ZuulSystem instances comparison"""
        self.assertNotEqual(
            self.system, "test",
            msg=f"System {self.system.name.value} should be different from str"
        )

    def test_system_str(self):
        """Testing ZuulSystem __str__ method"""
        self.assertEqual(str(self.system),
                         f"System: {self.name} (type: zuul)")

        self.assertEqual(str(self.other_system),
                         f"System: {self.name} (type: zuul)")

    def test_add_pipeline(self):
        """Testing ZuulSystem add pipeline method"""
        pipeline = Pipeline("check")
        self.system.add_pipeline(pipeline)
        self.assertEqual(len(self.system.pipelines.value), 1)
        self.assertEqual(pipeline, self.system.pipelines[0])

    def test_add_job(self):
        """Testing adding a new job to a system"""
        job = Job("test_job")
        self.system.add_job(job)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value[0])

    def test_add_source(self):
        """Testing adding a new source to a system"""
        source = Source("test_source", driver="jenkins")
        self.system.add_source(source)
        self.assertEqual(len(self.system.sources.value), 1)
        self.assertEqual(source, self.system.sources.value[0])


class TestJenkinsSystem(unittest.TestCase):
    """Testing the JenkinsSystem class"""
    def setUp(self):
        self.name = "test"
        self.system = JenkinsSystem(self.name)
        self.other_system = JenkinsSystem(self.name)

    def test_new_system_name(self):
        """Testing the type attribute of the JenkinsSystem class"""
        self.assertTrue(
            hasattr(self.system, 'name'), msg="System lacks name attribute")
        system_name = self.system.name.value
        error_msg = f"System name should be {self.name}, not {system_name}"
        self.assertEqual(self.system.name.value, self.name,
                         msg=error_msg)

    def test_new_system_type(self):
        """Testing the type attribute of the JenkinsSystem class"""
        self.assertTrue(
            hasattr(self.system, 'system_type'),
            msg="System lacks type attribute")
        system_type = self.system.system_type.value
        error_msg = f"System type should be jenkins, not {system_type}"
        self.assertEqual(self.system.name.value, self.name,
                         msg=error_msg)

    def test_system_comparison(self):
        """Testing new JenkinsSystem instances comparison"""
        self.assertEqual(
            self.system, self.other_system,
            msg=f"Systems {self.system.name.value} and \
{self.system.name.value} are not equal")

    def test_system_comparison_other_types(self):
        """Testing new JenkinsSystem instances comparison"""
        self.assertNotEqual(
            self.system, "test",
            msg=f"System {self.system.name.value} should be different from str"
        )

    def test_system_str(self):
        """Testing JenkinsSystem __str__ method"""
        self.assertEqual(str(self.system),
                         f"System: {self.name} (type: jenkins)")

        self.assertEqual(str(self.other_system),
                         f"System: {self.name} (type: jenkins)")

    def test_add_job(self):
        """Testing adding a new job to a system"""
        job = Job("test_job")
        self.system.add_job(job)
        self.assertEqual(len(self.system.jobs.value), 1)
        self.assertEqual(job, self.system.jobs.value[0])
