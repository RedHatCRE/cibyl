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
import logging

from cibyl.cli.argument import Argument
from cibyl.features import FeatureDefinition
from cibyl.plugins.openstack.features import OpenstackFeatureTemplate

LOG = logging.getLogger(__name__)


class HA(OpenstackFeatureTemplate, FeatureDefinition):
    """Highly available Openstack deployment with at least 2 controllers."""

    name = "HA"

    def __init__(self):
        super().__init__(self.name)

    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        ha_arg = Argument("controllers", arg_type=str,
                          description="Number of controller nodes",
                          func="get_deployment",
                          ranged=True, value=[">=2"])
        return {'controllers': ha_arg}


class IPV4(OpenstackFeatureTemplate, FeatureDefinition):
    """Openstack deployment using IPv4."""

    name = "IPV4"

    def __init__(self):
        super().__init__(self.name)

    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        ip_arg = Argument("ip_version", arg_type=str,
                          description="IP version used",
                          func="get_deployment",
                          value=["4"])
        return {'ip_version': ip_arg}


class IPV6(OpenstackFeatureTemplate, FeatureDefinition):
    """Openstack deployment using IPv6."""

    name = "IPV6"

    def __init__(self):
        super().__init__(self.name)

    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        ip_arg = Argument("ip_version", arg_type=str,
                          description="IP version used",
                          func="get_deployment",
                          value=["6"])
        return {'ip_version': ip_arg}


class DVR(OpenstackFeatureTemplate, FeatureDefinition):
    """Openstack deployment configured with 'Distributed Virtual Router'"""

    name = "DVR"

    def __init__(self):
        super().__init__(self.name)

    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        dvr_arg = Argument("dvr", arg_type=str,
                           description="DVR enabled",
                           func="get_deployment", value="True")
        return {'dvr': dvr_arg}
