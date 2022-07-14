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

from cibyl.plugins.openstack.sources.zuul.actions import DeploymentQuery


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
