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

from cibyl.sources.zuul.arguments import ArgumentReview


class TestArgumentReview(TestCase):
    """Tests for :class:`ArgumentReview`.
    """

    def test_is_tenants_requested(self):
        """Checks the arguments that make the tenants query be requested.
        """
        review = ArgumentReview()

        for arg in ('tenants',):
            review.is_tenants_query_requested(**{arg: None})

    def test_is_projects_requested(self):
        """Checks the arguments that make the projects query be requested.
        """
        review = ArgumentReview()

        for arg in ('projects',):
            review.is_projects_query_requested(**{arg: None})

    def test_is_pipelines_requested(self):
        """Checks the arguments that make the pipelines query be requested.
        """
        review = ArgumentReview()

        for arg in ('pipelines',):
            review.is_pipelines_query_requested(**{arg: None})

    def test_is_jobs_requested(self):
        """Checks the arguments that make the jobs query be requested.
        """
        review = ArgumentReview()

        for arg in ('jobs', 'job_url'):
            review.is_jobs_query_requested(**{arg: None})

    def test_is_variants_requested(self):
        """Checks the arguments that make the variants query be requested.
        """
        review = ArgumentReview()

        for arg in ('variants',):
            review.is_variants_query_requested(**{arg: None})

    def test_is_builds_requested(self):
        """Checks the arguments that make the builds query be requested.
        """
        review = ArgumentReview()

        for arg in ('builds', 'last_build', 'build_status'):
            self.assertTrue(review.is_builds_query_requested(**{arg: None}))

    def test_is_tests_requested(self):
        """Checks the arguments that make the tests query be requested.
        """
        review = ArgumentReview()

        for arg in ('tests', 'test_result', 'test_duration'):
            review.is_tests_query_requested(**{arg: None})
