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

from cibyl.plugins.openstack import Plugin
from cibyl.plugins.openstack.sources.zuul import DeploymentQuery


class TestDeploymentQuery(TestCase):
    """Tests for :class:`DeploymentQuery`.
    """

    @classmethod
    def setUpClass(cls):
        Plugin().extend_models()

    def test_release_filter(self):
        """Checks that jobs are filtered by their deployment's release.
        """

        def jobs(*_, **__):
            return [job]

        def variants(*_, **__):
            return [variant1, variant2]

        release_arg = Mock()
        release_arg.value = ['1.*']

        kwargs = {
            'release': release_arg
        }

        tenant = Mock()
        job = Mock()
        variant1 = Mock()
        variant2 = Mock()

        tenant.name = 'tenant'
        tenant.jobs = Mock()
        tenant.jobs.return_value = Mock()
        tenant.jobs.return_value.get = Mock()
        tenant.jobs.return_value.get.return_value = [job]

        job.tenant = tenant
        job.name = 'name'
        job.variants.return_value = Mock()
        job.variants.return_value.get = Mock()
        job.variants.return_value.get.return_value = [variant1, variant2]

        variant1.job = job
        variant1.parent = None
        variant1.name = 'variant1'
        variant1.branches = ['master']
        variant1.variables = {
            'rhos_release_version': '1.2'
        }

        variant2.job = job
        variant2.parent = None
        variant2.name = 'variant2'
        variant2.branches = ['other']
        variant2.variables = {
            'rhos_release_version': '2.0'
        }

        api = Mock()

        queries = Mock()
        queries.jobs = Mock()
        queries.jobs.side_effect = jobs
        queries.variants = Mock()
        queries.variants.side_effect = variants

        query = DeploymentQuery(api, queries=queries)

        result = query.perform_query(**kwargs)

        result_tenant = result[tenant.name]
        result_job = result_tenant.jobs.value[job.name]
        result_variants = result_job.variants.value

        # Check the that variant in the first release is the one returned
        self.assertEqual(1, len(result_variants))
        self.assertEqual(variant1.name, result_variants[0].name.value)
