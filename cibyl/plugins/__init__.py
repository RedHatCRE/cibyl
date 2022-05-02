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

from cibyl.exceptions.plugin import MissingPlugin
from cibyl.models.ci.environment import Environment

LOG = logging.getLogger(__name__)


def extend_models(plugin_name):
    try:
        LOG.info("Loading plugin: {}".format(plugin_name))
        loaded_plugin = __import__(f"cibyl.plugins.{plugin_name}",
                                   fromlist=[''])
        loaded_plugin.Plugin()._extend(Environment.API)
    except (ImportError, ModuleNotFoundError):
        raise MissingPlugin(plugin_name)
