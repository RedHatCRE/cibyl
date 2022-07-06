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
from unittest.mock import Mock, call

from cibyl.plugins.openstack.sources.zuul.actions import (DeploymentFiltering,
                                                          DeploymentGenerator,
                                                          DeploymentQuery,
                                                          SpecArgumentHandler)


class TestDeploymentGenerator(TestCase):
    """Tests for :class:`DeploymentGenerator`.
    """

    def test_no_release(self):
        """Checks that the release is not fetched if no arg for it is passed.
        """
        kwargs = {
        }

        release_search = Mock()
        release_search.search = Mock()

        variant = Mock()

        tools = Mock()
        tools.release_search = release_search

        generator = DeploymentGenerator(tools)

        deployment = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual('', deployment.release.value)

        release_search.search.assert_not_called()

    def test_adds_release_on_spec_arg(self):
        """Checks that the release is fetched if the 'spec' arg is passed.
        """
        kwargs = {
            'spec': None
        }

        variable = 'var'
        release = 'v1.0'

        release_search = Mock()
        release_search.search = Mock()
        release_search.search.return_value = (variable, release)

        variant = Mock()

        tools = Mock()
        tools.release_search = release_search

        generator = DeploymentGenerator(tools)

        deployment = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(release, deployment.release.value)

        release_search.search.assert_called_once_with(variant)

    def test_adds_release_on_release_arg(self):
        """Checks that the release is fetched if the 'release' arg is passed.
        """
        kwargs = {
            'release': None
        }

        variable = 'var'
        release = 'v1.0'

        release_search = Mock()
        release_search.search = Mock()
        release_search.search.return_value = (variable, release)

        variant = Mock()

        tools = Mock()
        tools.release_search = release_search

        generator = DeploymentGenerator(tools)

        deployment = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(release, deployment.release.value)

        release_search.search.assert_called_once_with(variant)


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


class TestDeploymentFiltering(TestCase):
    """Tests for :class:`DeploymentFiltering`.
    """

    def test_applies_release_filter(self):
        """Checks that the filter for releases is generated and applied.
        """
        release1 = '1'
        release2 = '2'

        release_arg = Mock()
        release_arg.value = release1

        kwargs = {
            'release': release_arg
        }

        deployment1 = Mock()
        deployment1.release.value = release1

        deployment2 = Mock()
        deployment2.release.value = release2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))


class TestDeploymentQuery(TestCase):
    """Tests for :class:`DeploymentQuery`.
    """

    def test_gets_deployment_for_all_variants(self):
        """Checks that the deployment is generated for all variants on all
        fetched jobs.
        """

        def jobs(api, **_):
            return [job1, job2]

        def variants(job, **_):
            if job == job1:
                return [variant1]

            if job == job2:
                return [variant2]

            raise NotImplementedError

        def models(variant, **_):
            if variant == variant1:
                return model1

            if variant == variant2:
                return model2

            raise NotImplementedError

        def deployments(variant, **_):
            if variant == variant1:
                return deployment1

            if variant == variant2:
                return deployment2

            raise NotImplementedError

        kwargs = {
        }

        deployment1 = Mock()
        deployment2 = Mock()

        model1 = Mock()
        model2 = Mock()

        variant1 = Mock()
        variant2 = Mock()

        job1 = Mock()
        job2 = Mock()

        api = Mock()

        dgen = Mock()
        dgen.generate_deployment_for = Mock()
        dgen.generate_deployment_for.side_effect = deployments

        argh = Mock()

        output = Mock()
        output.with_variant = Mock()
        output.with_variant.side_effect = models

        queries = Mock()
        queries.jobs = jobs
        queries.variants = variants

        tools = Mock()
        tools.deployment_generator = dgen
        tools.spec_arg_handler = argh
        tools.output_builder = output

        query = DeploymentQuery(api, queries, tools)
        query.perform_query(**kwargs)

        self.assertEqual(
            model1.deployment.value,
            deployment1
        )

        self.assertEqual(
            model2.deployment.value,
            deployment2
        )

        output.with_variant.assert_has_calls(
            [
                call(variant1),
                call(variant2)
            ]
        )

        dgen.generate_deployment_for.assert_has_calls(
            [
                call(variant1),
                call(variant2)
            ]
        )
