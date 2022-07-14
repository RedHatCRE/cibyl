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

from cibyl.plugins.openstack.sources.zuul.deployments.generator import \
    DeploymentGenerator


class TestReleaseArgument(TestCase):
    """Tests how the '--release' argument affects :class:`DeploymentGenerator`.
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


class TestInfraTypeArgument(TestCase):
    """Tests how the '--infra-type' argument affects
    :class:`DeploymentGenerator`.
    """
