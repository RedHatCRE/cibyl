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
from copy import deepcopy
from unittest import TestCase

from cibyl.models.ci.environment import Environment
from cibyl.models.ci.job import Job
from cibyl.models.ci.printers.raw import CIRawPrinter
from cibyl.models.ci.system import System, JobsSystem
from cibyl.plugins import extend_models
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.utils import translate_topology_string


class TestOpenstackPlugin(TestCase):
    """Test OpenStack plugin"""

    @classmethod
    def setUpClass(cls):
        System.API = deepcopy(JobsSystem.API)

    def test_extend_models(self):
        """Test extend_models method"""
        self.assertIsNone(extend_models("openstack"))
        environment = Environment("test")
        environment.add_system(name="test", system_type='jenkins')
        self.assertIn(
            'deployment',
            environment.systems[0].jobs.attr_type.API)


class TestJobWithPlugin(TestCase):
    """Testing Job CI model with openstack plugin"""

    @classmethod
    def setUpClass(cls):
        System.API = deepcopy(JobsSystem.API)

    def setUp(self):
        extend_models("openstack")
        self.deployment = Deployment(17.0, "test", {}, {})
        self.deployment2 = Deployment(17.1, "test", {}, {})
        self.job = Job("job1", "url1")
        self.job2 = Job("job2", "url2")

    def test_add_deployment(self):
        """Test add_deployment method of Job."""
        self.job.add_deployment(self.deployment)
        self.assertEqual(self.job.deployment.value.release,
                         self.deployment.release)

    def test_merge(self):
        """Test merge method of Job with deployment."""
        self.job2.add_deployment(self.deployment2)
        self.job.merge(self.job2)
        self.assertEqual(self.job.deployment.value.release.value,
                         self.deployment2.release.value)

    def test_str(self):
        """Test string representation of Job with deployment."""
        self.job.add_deployment(self.deployment)

        printer = CIRawPrinter(verbosity=2)
        result = printer.print_job(self.job)

        self.assertIn("Release: ", result)
        self.assertIn("Infra type: ", result)

    def test_str_no_deployment(self):
        """Test string representation of Job without deployment."""
        printer = CIRawPrinter(verbosity=2)
        result = printer.print_job(self.job)

        self.assertNotIn("Release: ", result)
        self.assertNotIn("Infra type: ", result)


class TestOpenstackPluginUtils(TestCase):
    """Test openstack plugin utils module."""
    def test_translate_toplogy_string(self):
        """Test normal usage of translate_topology_string function."""
        input_str = "1comp_2cont_2ceph_3freeipa_5net_1novactl"
        expected = "compute:1,controller:2,ceph:2,freeipa:3,networker:5,"
        expected += "novacontrol:1"
        output = translate_topology_string(input_str)
        self.assertEqual(expected, output)

    def test_translate_toplogy_string_non_existing(self):
        """Test test_translate_toplogy_string with an unknown type."""
        input_str = "1comp_2cont_2ceph_3freeipa_1unk"
        expected = "compute:1,controller:2,ceph:2,freeipa:3,unk:1"
        output = translate_topology_string(input_str)
        self.assertEqual(expected, output)

    def test_translate_toplogy_string_malformed_component(self):
        """Test test_translate_toplogy_string with an malformed comonent."""
        input_str = "1comp_2cont_2ceph_3freeipa_unk"
        expected = "compute:1,controller:2,ceph:2,freeipa:3"
        output = translate_topology_string(input_str)
        self.assertEqual(expected, output)
