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

from cibyl.features import FeatureTemplate

LOG = logging.getLogger(__name__)


class OpenstackFeatureTemplate(FeatureTemplate):
    """Skeleton for an openstack specific feature."""

    def __init__(self, name: str):
        self.name = name

    def get_method_to_query(self):
        return "get_deployment"
