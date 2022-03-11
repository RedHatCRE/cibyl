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

from cibyl.models.ci.environment import Environment
from cibyl.models.ci.system import JenkinsSystem, ZuulSystem


class TestEnvironment(unittest.TestCase):
    """Testing Environment CI model"""

    def setUp(self):
        self.name = "test_env"
        self.env = Environment(self.name)

    def test_new_environment_name(self):
        """Testing new Environment name attribute"""
        attribute_name = 'name'
        test_name_bool = hasattr(self.env, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"Environment lacks an attribute: {attribute_name}")
        self.assertEqual(
            self.env.name.value, self.name,
            msg=f"Environment name is {self.env.name.value} \
instead of {self.name}")

    def test_new_environment_systems(self):
        """Testing new Environment name systems attribute"""
        attribute_name = 'systems'
        test_name_bool = hasattr(self.env, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg=f"Environment lacks an attribute: {attribute_name}")

    def test_add_systems(self):
        """Testing adding systems to environment"""
        self.env.add_system("zuul_sys", "zuul")
        self.env.add_system("jenkins_sys", "jenkins")
        self.assertEqual(2, len(self.env.systems.value))
        self.assertEqual("zuul_sys", self.env.systems.value[0].name.value)
        self.assertEqual("jenkins_sys", self.env.systems.value[1].name.value)

    def test_str_environment(self):
        """Testing environment str method"""
        self.assertEqual(f"Environment: {self.name}",
                         str(self.env))

    def test_add_systems_constructor(self):
        """Testing passing systems to environment constructor"""
        zuul = ZuulSystem("zuul_sys")
        jenkins = JenkinsSystem("jenkins_sys")
        env = Environment("systems", systems=[zuul, jenkins])
        self.assertEqual(2, len(env.systems.value))
        self.assertEqual("zuul_sys", env.systems.value[0].name.value)
        self.assertEqual("jenkins_sys", env.systems.value[1].name.value)
