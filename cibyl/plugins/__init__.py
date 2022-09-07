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
import os
from abc import ABC, abstractmethod
from typing import Callable, List

from cibyl.exceptions.plugin import MissingPlugin
from cibyl.models.model import Model
from cibyl.outputs.cli.printer import JSON, ColoredPrinter, SerializedPrinter
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source_factory import SourceFactory
from cibyl.utils.files import FileSearch
from cibyl.utils.filtering import apply_filters
from cibyl.utils.reflection import get_classes_in, load_module

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


def get_plugin_sources(plugin_module_path):
    result = []

    file_search = FileSearch(plugin_module_path)
    file_search.with_recursion()
    file_search.with_extension('.py')

    for module_path in file_search.get():
        result += apply_filters(
            get_classes_in(load_module(module_path)),
            lambda cls: issubclass(cls, SourceExtension),
            lambda cls: cls is not SourceExtension
        )

    return result


def extend_source(plugin_module_path):
    for plugin_source in get_plugin_sources(plugin_module_path):
        SourceFactory.extend_source(plugin_source)


def enable_plugins(plugins: list = None) -> List[Callable]:
    """Enable plugins based on a given list of plugins.

    :returns: List of functions that add subparsers to cibyl cli."""
    subpasers_functions = []
    if plugins:
        for plugin in plugins:
            LOG.debug("Loading plugin: %s", plugin)
            plugin_module = get_plugin_module(plugin)
            plugin_module.Plugin().extend_models()
            plugin_module.Plugin().register_features()
            plugin_module_path = get_plugin_module_path(plugin_module)
            extend_source(plugin_module_path)
            plugin_module.Plugin().extend_query_types()
            functions = plugin_module.Plugin().get_subparsers_creators()
            subpasers_functions.extend(functions)
    return subpasers_functions


class PluginTemplate(ABC):
    """Abstract class to define the actions a plugin should take."""

    @abstractmethod
    def extend_models(self) -> None:
        """Extend models' API with product specific information."""
        raise NotImplementedError

    def get_subparsers_creators(self) -> List[Callable]:
        """Collect a list of functions from the plugin that will be used to
        extend Cibyl's cli with additional subcommands. All functions returned
        by this method must take an ArgumentParser object as an argument."""
        return []

    def register_features(self) -> None:
        """Add the path of the features found in this plugin to the
        features module."""
        pass

    @abstractmethod
    def extend_query_types(self) -> None:
        """Register the plugin function to deduce the type of query."""
        raise NotImplementedError


class PluginPrinterTemplate(ABC):
    """Abstract class to define the output formats a plugin should support."""

    @abstractmethod
    def as_text(
        self,
        model: Model,
        config: ColoredPrinter.Config
    ) -> str:
        """Makes the plugin give a plain/custom textual representation on
        the provided model. It is up to the plugin to check the model's type
        and decide on more specific actions from it.

        :param model: The model to print.
        :param config: Configuration to follow.
        :return: Textural representation of the model.
        :raises NotImplementedError: If the model type is not supported.
        """
        raise NotImplementedError

    @abstractmethod
    def as_json(
        self,
        model: Model,
        provider: JSON,
        config: SerializedPrinter.Config
    ) -> str:
        """Makes the plugin give a json representation on the provided model.
        It is up to the plugin to check the model's type and decide on more
        specific actions from it.

        :param model: The model to print.
        :param provider: JSON implementation the printer gets to use.
        :param config: Configuration to follow.
        :return: JSON representation of the model.
        :raises NotImplementedError: If the model type is not supported.
        """
        raise NotImplementedError
