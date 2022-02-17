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

import unittest

from cibyl.models.ci.system import System, ZuulModel, JenkinsModel

class TestSystem(unittest.TestCase):

    def test_new_system_name(self):
        system = System("test", "test_type")
        attribute_name = 'name'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg="System lacks an attribute: {}".format(attribute_name))
        self.assertEqual(system.name.value, "test")
        system_name = system.name.value
        self.assertEqual(system_name, "test",
                         msg=f"Name of system should be test, not {system_name}")

    def test_new_system_type(self):
        system = System("test", "test_type")
        attribute_name = 'type'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"System lacks an attribute: {attribute_name}")
        type_name = system.type.value
        self.assertEqual(type_name, "test_type",
                         msg=f"Type of system should be test_type, not {type_name}")


class TestZuulSystem(unittest.TestCase):

    def test_new_system_name(self):
        system = ZuulModel("test")
        attribute_name = 'name'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg="Zuul system lacks an attribute: {}".format(attribute_name))
        self.assertEqual(system.name.value, "test")
        system_name = system.name.value
        self.assertEqual(system_name, "test",
                         msg=f"Name of system should be test, not {system_name}")

    def test_new_system_type(self):
        system = System("test", "test_type")
        attribute_name = 'type'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"Zuul system lacks an attribute: {attribute_name}")
        type_name = system.type.value
        self.assertEqual(type_name, "zuul",
                         msg=f"Type of system should be zuul, not {type_name}")


class TestJenkinsSystem(unittest.TestCase):

    def test_new_system_name(self):
        system = JenkinsModel("test")
        attribute_name = 'name'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg="Jenkins system lacks an attribute: {}".format(attribute_name))
        self.assertEqual(system.name.value, "test")
        system_name = system.name.value
        self.assertEqual(system_name, "test",
                         msg=f"Name of system should be test, not {system_name}")

    def test_new_system_type(self):
        system = System("test", "test_type")
        attribute_name = 'type'
        test_name_bool = hasattr(system, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"System lacks an attribute: {attribute_name}")
        type_name = system.type.value
        self.assertEqual(type_name, "jenkins",
                         msg=f"Type of system should be jenkins, not {type_name}")
