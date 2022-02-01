# Copyright 2022 Red Hat
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
import logging

from cibyl.models.openstack.deployment import Deployment
from cibyl.plugins.interface import PluginInterface
from cibyl.value import Value


LOG = logging.getLogger(__name__)


class Openstack(PluginInterface):

    def extend(self, environments=[]):
        for env in environments:
            for system in env.systems:
                # TODO(abregman) Add support for Zuul
                if system.type.data.lower() == "zuul":
                    pass
                elif system.type.data.lower() == 'jenkins':
                    for job in system.jobs:
                        job.deployment = Value(type=Deployment,
                                               name='deployment')
        LOG.debug("extended entities with OpenStack plugin")
