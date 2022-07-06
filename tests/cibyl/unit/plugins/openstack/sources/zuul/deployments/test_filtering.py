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

from cibyl.plugins.openstack.sources.zuul.deployments.filtering import \
    DeploymentFiltering


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
