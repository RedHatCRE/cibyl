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


class Inspector(OpenstackFeatureTemplate, FeatureDefinition):
    """Discovering hardware properties for a node managed by Ironic"""

    name = "ironic-inspector"

    def __init__(self):
        super().__init__(self.name)

    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        inspector_arg = Argument("ironic_inspector", arg_type=str,
                                 description="Ironic Inspector",
                                 func="get_deployment", value="True")
        return {'ironic_inspector': inspector_arg}
