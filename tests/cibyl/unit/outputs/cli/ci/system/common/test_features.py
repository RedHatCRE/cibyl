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

import cibyl.outputs.cli.ci.system.common.features as features_query
from cibyl.cli.query import QueryType


class TestIsFeaturesQuery(TestCase):
    """Tests for :func:`features_query.is_features_query`
    """

    def test_none_query(self):
        """Checks result is false if the query passed is none.
        """
        query = QueryType.NONE

        self.assertFalse(features_query.is_features_query(query))

    def test_jobs_query(self):
        """Checks result is false if the query passed is JOBS.
        """
        query = QueryType.JOBS

        self.assertFalse(features_query.is_features_query(query))

    def test_features_query(self):
        """Checks result is true if the query passed is FEATURES.
        """
        query = QueryType.FEATURES

        self.assertTrue(features_query.is_features_query(query))

    def test_features_jobs_query(self):
        """Checks result is true if the query passed is FEATURES and JOBS.
        """
        query = QueryType.FEATURES | QueryType.JOBS

        self.assertTrue(features_query.is_features_query(query))

    def test_builds_jobs_query(self):
        """Checks result is false if the query passed is BUILDS and JOBS.
        """
        query = QueryType.BUILDS | QueryType.JOBS

        self.assertFalse(features_query.is_features_query(query))


class TestIsPureFeaturesQuery(TestCase):
    """Tests for :func:`features_query.is_pure_features_query`
    """

    def test_none_query(self):
        """Checks result is false if the query passed is none.
        """
        query = QueryType.NONE

        self.assertFalse(features_query.is_pure_features_query(query))

    def test_jobs_query(self):
        """Checks result is false if the query passed is JOBS.
        """
        query = QueryType.JOBS

        self.assertFalse(features_query.is_pure_features_query(query))

    def test_features_query(self):
        """Checks result is true if the query passed is FEATURES.
        """
        query = QueryType.FEATURES

        self.assertTrue(features_query.is_pure_features_query(query))

    def test_features_jobs_query(self):
        """Checks result is false if the query passed is FEATURES and JOBS.
        """
        query = QueryType.FEATURES | QueryType.JOBS

        self.assertFalse(features_query.is_pure_features_query(query))

    def test_builds_jobs_query(self):
        """Checks result is false if the query passed is BUILDS and JOBS.
        """
        query = QueryType.BUILDS | QueryType.JOBS

        self.assertFalse(features_query.is_pure_features_query(query))
