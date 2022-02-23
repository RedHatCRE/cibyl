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
import unittest

from cibyl.models.ci.environment import Environment


class TestEnvironment(unittest.TestCase):
    """Testing Environment CI model"""

    def test_new_environment_name(self):
        """Testing new Environment name attribute"""
        env_name = "test_env"
        env = Environment(name=env_name)
        attribute_name = 'name'
        test_name_bool = hasattr(env, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg="Environment lacks an attribute: {}".format(attribute_name))
        self.assertEqual(env.name.value, env_name,
                         msg="Environment name is {} instead of {}".format(
                             env.name.value, env_name))

    def test_new_environment_systems(self):
        """Testing new Environment name systems attribute"""
        env_name = "test_env"
        env = Environment(name=env_name)
        attribute_name = 'systems'
        test_name_bool = hasattr(env, attribute_name)
        self.assertTrue(
            test_name_bool,
            msg="Environment lacks an attribute: {}".format(attribute_name))
