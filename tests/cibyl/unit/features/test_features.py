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
import inspect
import os
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch

from cibyl import features
from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.exceptions.source import NoValidSources
from cibyl.features import (FeatureTemplate, get_feature,
                            get_string_all_features, is_feature_class,
                            load_features)
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.system import JobsSystem
from cibyl.sources.jenkins import Jenkins
from cibyl.sources.source import Source
from cibyl.utils.colors import Colors
from tests.cibyl.unit.features.data.testing import Feature1, Feature2
from tests.cibyl.utils import RestoreAPIs


class TestFeaturesLoader(RestoreAPIs):
    """Testing FeaturesLoader class"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.feature_path = os.path.dirname(inspect.getfile(Feature1))
        load_features(feature_paths=[cls.feature_path])

    def test_is_feature_class(self):
        """Test that the is_feature_class function properly filters the classes
        that correspond to features."""
        self.assertTrue(is_feature_class(Feature1))
        self.assertTrue(is_feature_class(Feature2))
        # is class, but not feature
        self.assertFalse(is_feature_class(TestCase))
        # is not class
        self.assertFalse(is_feature_class(TestCase))
        # is abstract class
        self.assertFalse(is_feature_class(FeatureTemplate))

    def test_get_feature_successful(self):
        """Test that the FeaturesLoader properly gets the loaded features by
        name"""
        feature1 = get_feature("Feature1")
        # test lowercase/uppercase cases
        feature2 = get_feature("feature2")
        feature3 = get_feature("FEATURE3")
        self.assertEqual(feature1.name, "Feature1")
        self.assertEqual(feature2.name, "Feature2")
        self.assertEqual(feature3.name, "Feature3")

    def test_get_feature_inexistent(self):
        """Test that an error is raised when a non-existent feature is
        requested."""
        msg = "No feature non-existing. Choose one of the following "
        msg += "features:\n"
        msg += "\nTesting:\n * Feature1 - Feature for testing1\n"
        msg += " * Feature2 - Feature for testing2"
        with self.assertRaises(InvalidArgument, msg=msg):
            get_feature("non-existing")

    def test_get_string_all_features(self):
        """Test that get_string_all_features provides the correct string
        representation."""
        output = get_string_all_features()
        expected = f"\n\n{Colors.blue('Testing')}:\n"
        expected += f"{Colors.red(' * ')}{Colors.blue('Feature1')}"
        expected += f"{Colors.red(' - Feature for testing1')}\n"
        expected += f"{Colors.red(' * ')}{Colors.blue('Feature2')}"
        expected += f"{Colors.red(' - Feature for testing2')}\n"
        expected += f"{Colors.red(' * ')}{Colors.blue('Feature3')}"
        self.assertEqual(output, expected)

    def test_add_feature_location(self):
        """Test that add_feature_location modifies the features_locations
        attribute of FeaturesLoader."""
        original_location = deepcopy(features.features_locations)
        features.add_feature_location(self.feature_path)
        self.assertEqual(len(features.features_locations), 2)
        self.assertIn(self.feature_path, features.features_locations)
        features.features_locations = deepcopy(original_location)

    @patch('cibyl.features.get_source_instance_from_method')
    @patch('cibyl.features.source_information_from_method')
    @patch.object(Jenkins, 'get_jobs')
    def test_query(self, jenkins_jobs, source_information_patched,
                   get_source_instance_patched):
        """Test a successful query using the query method of the
        FeatureTemplate class."""
        job = Job('job')
        jenkins_jobs.return_value = AttributeDictValue('jobs',
                                                       value={'job': job})
        source_information_patched.return_value = ""
        source = Jenkins(url='url')
        get_source_instance_patched.return_value = source
        system = JobsSystem('test', 'test-type', sources=[source])
        feature1 = get_feature("Feature1")
        result = feature1.query(system)
        self.assertTrue(system.is_queried())
        self.assertEqual(len(result), 1)
        self.assertEqual(result['job'].name.value, 'job')

    def test_query_no_sources(self):
        """Test that query method of the FeatureTemplate class returns None if
        no source was found."""
        system = JobsSystem('test', 'test-type')
        feature1 = get_feature("Feature1")
        with self.assertRaises(NoValidSources):
            feature1.query(system)

    def test_query_no_sources_support_query(self):
        """Test that query method of the FeatureTemplate class returns None if
        no source was found."""
        source = Source('test')
        system = JobsSystem('test', 'test-type', sources=[source])
        feature1 = get_feature("Feature1")
        self.assertIsNone(feature1.query(system))

    @patch('cibyl.features.get_source_instance_from_method')
    @patch('cibyl.features.source_information_from_method')
    @patch.object(Jenkins, 'get_jobs')
    def test_query_sources_exception(self, jenkins_jobs,
                                     source_information_patched,
                                     get_source_instance_patched):
        """Test that query method of the FeatureTemplate class returns None if
        all sources raises errors when queried."""
        source = Jenkins(url='url')
        jenkins_jobs.side_effect = JenkinsError
        source_information_patched.return_value = ""
        get_source_instance_patched.return_value = source
        system = JobsSystem('test', 'test-type', sources=[source])
        feature1 = get_feature("Feature1")
        self.assertIsNone(feature1.query(system))
