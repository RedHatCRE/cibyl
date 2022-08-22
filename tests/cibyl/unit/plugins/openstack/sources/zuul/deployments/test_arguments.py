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

from cibyl.plugins.openstack.sources.zuul.deployments.arguments import (
    ArgumentReview, SpecArgumentHandler)


class TestArgumentReview(TestCase):
    """Tests for :class:`ArgumentReview`.
    """

    def test_is_release_requested(self):
        """Checks the conditions required for the release to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_release_requested(**{}))

        self.assertTrue(review.is_release_requested(**{'release': None}))
        self.assertTrue(review.is_release_requested(**{'spec': None}))

    def test_is_infra_type_requested(self):
        """Checks the conditions required for the infra type to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_infra_type_requested(**{}))

        self.assertTrue(review.is_infra_type_requested(**{'infra_type': None}))
        self.assertTrue(review.is_infra_type_requested(**{'spec': None}))

    def test_is_nodes_requested(self):
        """Checks the conditions required for the nodes list to be
        requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_nodes_requested(**{}))

        self.assertTrue(review.is_nodes_requested(**{'controllers': None}))
        self.assertTrue(review.is_nodes_requested(**{'nodes': None}))
        self.assertTrue(review.is_nodes_requested(**{'spec': None}))

    def test_is_topology_requested(self):
        """Checks the conditions required for the topology to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_topology_requested(**{}))

        self.assertTrue(review.is_topology_requested(**{'topology': None}))
        self.assertTrue(review.is_topology_requested(**{'spec': None}))

    def test_is_cinder_backend_requested(self):
        """Checks the conditions required for the cinder backend to be
        requested.
        """
        review = ArgumentReview()

        self.assertFalse(
            review.is_cinder_backend_requested(**{})
        )

        self.assertTrue(
            review.is_cinder_backend_requested(**{'cinder_backend': None})
        )

        self.assertTrue(
            review.is_cinder_backend_requested(**{'spec': None})
        )

    def test_is_network_backend_requested(self):
        """Checks the conditions required for the network backend to be
        requested.
        """
        review = ArgumentReview()

        self.assertFalse(
            review.is_network_backend_requested(**{})
        )

        self.assertTrue(
            review.is_network_backend_requested(**{'network_backend': None})
        )

        self.assertTrue(
            review.is_network_backend_requested(**{'spec': None})
        )

    def test_is_ip_version_requested(self):
        """Checks the conditions required for the ip version to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_ip_version_requested(**{}))

        self.assertTrue(review.is_ip_version_requested(**{'ip_version': None}))
        self.assertTrue(review.is_ip_version_requested(**{'spec': None}))

    def test_is_tls_everywhere_requested(self):
        """Checks the conditions required for tls everywhere to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_tls_everywhere_requested(**{}))

        self.assertTrue(review.is_tls_everywhere_requested(**{'spec': None}))

    def test_is_ml2_driver_requested(self):
        """Checks the conditions required for ml2 driver to be requested.
        """
        review = ArgumentReview()

        self.assertFalse(review.is_ml2_driver_requested(**{}))

        self.assertTrue(review.is_ml2_driver_requested(**{'spec': None}))
        self.assertTrue(review.is_ml2_driver_requested(**{'ml2_driver': None}))


class TestSpecArgumentHandler(TestCase):
    """Tests for :class:`SpecArgumentHandler`.
    """

    def test_jobs_but_empty_spec(self):
        """Check that if no job is indicated on the 'spec' arg, the jobs
        from the 'jobs' arg will be used.
        """
        job = 'job'

        kwargs = {
            'jobs': job,
            'spec': None
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.JOBS,
            handler.get_target_jobs(**kwargs)
        )

    def test_spec_but_empty_jobs(self):
        """Check that if no job is indicated on the 'jobs' arg, the jobs
        from the 'spec' arg will be used.
        """
        job = 'job'

        kwargs = {
            'jobs': None,
            'spec': job
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.SPEC,
            handler.get_target_jobs(**kwargs)
        )

    def test_empty_spec_and_jobs(self):
        """Check that if both arguments are empty, then all jobs will be
        targeted.
        """
        kwargs = {
            'jobs': None,
            'spec': None
        }

        handler = SpecArgumentHandler()

        # Empty means all jobs
        self.assertEqual(
            SpecArgumentHandler.Option.EMPTY,
            handler.get_target_jobs(**kwargs)
        )

    def test_different_spec_and_jobs(self):
        """Checks that if both arguments have a value, the 'spec' on is
        preferred.
        """
        job1 = 'job1'
        job2 = 'job2'

        kwargs = {
            'jobs': job1,
            'spec': job2
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.SPEC,
            handler.get_target_jobs(**kwargs)
        )

    def test_spec_but_no_jobs(self):
        """Checks if the 'spec' argument is present but the 'jobs' is not,
        then the jobs from the 'spec' argument are returned.
        """
        job = 'job'

        kwargs = {
            'spec': job
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.SPEC,
            handler.get_target_jobs(**kwargs)
        )

    def test_jobs_but_no_spec(self):
        """Checks if the 'jobs' argument is present but the 'spec' is not,
        then the jobs from the 'jobs' argument are returned.
        """
        job = 'job'

        kwargs = {
            'jobs': job
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.JOBS,
            handler.get_target_jobs(**kwargs)
        )

    def test_neither_argument(self):
        """Checks that nothing is returned if neither argument is present.
        """
        kwargs = {
        }

        handler = SpecArgumentHandler()

        self.assertEqual(
            SpecArgumentHandler.Option.NONE,
            handler.get_target_jobs(**kwargs)
        )
