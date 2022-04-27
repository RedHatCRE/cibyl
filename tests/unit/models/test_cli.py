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

from cibyl.models.cli import get_query_type, QueryType


class TestGetQueryType(TestCase):
    def test_get_none(self):
        """Checks that "None" is returned if no argument is passed.
        """
        args = {
        }

        self.assertEqual(QueryType.NONE, get_query_type(**args))

    def test_get_tenant(self):
        """Checks that "Tenants" is returned for "--tenants".
        """
        args = {
            'tenants': None
        }

        self.assertEqual(QueryType.TENANTS, get_query_type(**args))

    def test_get_jobs(self):
        """Checks that "Jobs" is returned for "--jobs", winning over
        "--tenants".
        """
        args = {
            'tenants': None,
            'jobs': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_builds(self):
        """Checks that "Builds" is returned for "--builds", winning over
        "--jobs".
        """
        args = {
            'jobs': None,
            'builds': None
        }

        self.assertEqual(QueryType.BUILDS, get_query_type(**args))
