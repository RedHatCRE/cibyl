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

from cibyl.sources.jenkins import Jenkins
from cibyl.sources.zuul.source import Zuul
from cibyl.utils.source_methods_store import SourceMethodsStore


class TestSourceMethodsStore(TestCase):
    """Test SourceMethodsStore class."""

    def setUp(self):
        self.cache = SourceMethodsStore()
        self.jenkins = Jenkins(url="", name="jenkins_source")
        self.zuul = Zuul(api=None, name="zuul_source", driver="zuul", url="")

    def test_add_call(self):
        """Test add_call method."""
        jenkins_get_jobs = self.jenkins.get_jobs
        self.cache.add_call(jenkins_get_jobs)
        self.assertEqual(self.cache.cache,
                         set([("jenkins_source", "get_jobs")]))

    def test_add_multiple_calls(self):
        """Test add_call method."""
        jenkins_get_jobs = self.jenkins.get_jobs
        zuul_get_builds = self.zuul.get_builds
        self.cache.add_call(jenkins_get_jobs)
        self.cache.add_call(zuul_get_builds)
        self.assertEqual(self.cache.cache,
                         set([("jenkins_source", "get_jobs"),
                              ("zuul_source", "get_builds")
                              ]))

    def test_has_been_called(self):
        """Test has_been_called method."""
        jenkins_get_jobs = self.jenkins.get_jobs
        zuul_get_builds = self.zuul.get_builds
        self.cache.add_call(jenkins_get_jobs)
        self.cache.add_call(zuul_get_builds)
        self.assertTrue(self.cache.has_been_called(jenkins_get_jobs))
        self.assertTrue(self.cache.has_been_called(zuul_get_builds))
