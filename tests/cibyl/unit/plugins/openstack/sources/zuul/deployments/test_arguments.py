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

from cibyl.plugins.openstack.sources.zuul.deployments.arguments import \
    SpecArgumentHandler


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
