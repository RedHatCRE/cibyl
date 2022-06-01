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

from cibyl.exceptions.config import NonSupportedSourceType
from cibyl.sources.elasticsearch.api import ElasticSearch
from cibyl.sources.jenkins import Jenkins
from cibyl.sources.jenkins_job_builder import JenkinsJobBuilder
from cibyl.sources.source_factory import SourceFactory
from cibyl.sources.zuul.source import Zuul


class TestSourceFactory(TestCase):
    """Test for the SourceFactory class."""

    def test_create_jenkins_source(self):
        """Checks that a jenkins source is created."""
        source = SourceFactory.create_source("jenkins", "jenkins_source",
                                             driver="jenkins", url="url")
        self.assertTrue(isinstance(source, Jenkins))
        self.assertEqual(source.name, "jenkins_source")
        self.assertEqual(source.driver, "jenkins")
        self.assertEqual(source.url, "url")

    def test_create_elasticsearch_source(self):
        """Checks that a elasticsearch source is created."""
        source = SourceFactory.create_source("elasticsearch", "elastic_source",
                                             driver="elastic",
                                             url="url")
        self.assertTrue(isinstance(source, ElasticSearch))
        self.assertEqual(source.name, "elastic_source")
        self.assertEqual(source.driver, "elastic")
        self.assertEqual(source.url, "url")

    def test_create_jenkins_job_builder_source(self):
        """Checks that a jenkins_job_builder source is created."""
        source = SourceFactory.create_source("jenkins_job_builder",
                                             "jjb_source",
                                             driver="jjb")
        self.assertTrue(isinstance(source, JenkinsJobBuilder))
        self.assertEqual(source.name, "jjb_source")
        self.assertEqual(source.driver, "jjb")

    def test_create_zuul_source(self):
        """Checks that a zuul source is created."""
        source = SourceFactory.create_source("zuul", "zuul_source",
                                             driver="zuul", url="url")
        self.assertTrue(isinstance(source, Zuul))
        self.assertEqual(source.name, "zuul_source")
        self.assertEqual(source.driver, "zuul")
        self.assertEqual(source.url, "url")

    def test_create_unknown_source(self):
        """Checks that an exception is raise if the source type is unknown."""
        self.assertRaises(NonSupportedSourceType,
                          SourceFactory.create_source,
                          "unknown", "zuul_source")


class TestExtendSource(TestCase):
    """Tests for :func:`SourceFactory.extend_source`."""

    def test_extend_zuul_source(self):
        """Checks that a Zuul source gets extended.
        """
        source = Mock()
        source.__name__ = 'Zuul'
        source.__test = Mock()
        source.test = Mock()

        SourceFactory.extend_source(source)

        self.assertFalse(hasattr(Zuul, '__test'))

        self.assertTrue(hasattr(Zuul, 'test'))
        self.assertEqual(Zuul.test, source.test)
