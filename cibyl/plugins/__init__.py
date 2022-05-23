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
import inspect
import logging
import os

from cibyl.exceptions.plugin import MissingPlugin
from cibyl.sources.source_factory import SourceFactory

LOG = logging.getLogger(__name__)


def get_plugin_module(plugin_name: str):
    """Returns plugin module based on a given plugin N

       :param plugin_name: the name of the plugin
       :type plugin_name: str
    """
    try:
        return __import__(f"cibyl.plugins.{plugin_name}",
                          fromlist=[''])
    except (ImportError, ModuleNotFoundError):
        raise MissingPlugin(plugin_name)


def get_plugin_module_path(plugin_module):
    return os.path.join(os.path.dirname(os.path.abspath(
        plugin_module.__file__)), 'sources')


def is_plugin_class(class_obj):
    return inspect.isclass(class_obj) and \
            "sources" in class_obj.__module__


def extend_source(plugin_name, plugin_module_path):
    plugin_sources = []
    for py in [f[:-3] for f in os.listdir(plugin_module_path)
               if f.endswith('.py') and f != '__init__.py']:
        mod = __import__('.'.join(
            [f"cibyl.plugins.{plugin_name}.sources", py]), fromlist=[py])
        new_element = [source_tuple[1] for source_tuple in
                       inspect.getmembers(mod, is_plugin_class)]
        plugin_sources.extend(new_element)
    for plugin_source in plugin_sources:
        SourceFactory.extend_source(plugin_source)


def enable_plugins(plugins: list = None):
    """Enable plugins based on a given list of plugins"""
    if plugins:
        for plugin in plugins:
            LOG.debug("Loading plugin: %s", plugin)
            plugin_module = get_plugin_module(plugin)
            plugin_module.Plugin().extend_models()
            plugin_module_path = get_plugin_module_path(plugin_module)
            extend_source(plugin, plugin_module_path)
            plugin_module.Plugin().extend_query_types()
