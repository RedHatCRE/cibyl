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
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from inspect import isclass
from typing import Optional, Type, Union

from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.features import MissingFeature
from cibyl.exceptions.source import NoSupportedSourcesFound, SourceException
from cibyl.models.ci.base.system import System
from cibyl.sources.source import (get_source_instance_from_method,
                                  select_source_method,
                                  source_information_from_method)
from cibyl.utils.colors import Colors
from cibyl.utils.files import FileSearch
from cibyl.utils.reflection import get_classes_in, load_module

LOG = logging.getLogger(__name__)

MODULE_PATTERN = re.compile(r"([a-zA-Z][a-zA-Z_]*)\.py")


def is_feature_class(symbol: object) -> bool:
    """Check whether the symbols imported from a module correspond to
    classes defining a feature. We assume that the symbol in question
    defines a feature if it inherits from the FeatureDefinition class.

    :param symbol: An imported symbol to check
    :returns: Whether the symbol defines a feature
    """
    return isclass(symbol) and issubclass(symbol, FeatureDefinition) and \
        symbol is not FeatureDefinition


# have the core features folder as the default location to search for
# features, since __path__ is a list this can be easily extended through
# plugins
features_locations = __path__
features_by_category = defaultdict(list)
all_features = {}


def add_feature_location(location: str) -> None:
    """Add an additional location where to find features."""
    features_locations.append(location)


def load_features(feature_paths: Optional[list] = None) -> None:
    global features_locations
    if feature_paths:
        features_locations = feature_paths
    for location in features_locations:
        file_search = FileSearch(location)
        file_search.with_recursion()
        file_search.with_extension('.py')
        # avoid trying to import this module, since it'll give problems with
        # the usage of __path__ variable
        file_search.with_excluded(['__init__'])
        for module_path in file_search.get():
            try:
                module = load_module(module_path)
            except Exception as ex:
                msg = f"Could not load feature from module {module_path}"
                msg += f" in path {location}"
                raise MissingFeature(msg) from ex
            features = get_classes_in(module, predicate=is_feature_class,
                                      return_name=True)
            module_name = module.__name__
            for feature_name, feature in features:
                all_features[feature.name.lower()] = feature
                features_by_category[module_name].append(feature.name)


def get_string_all_features() -> str:
    """Get a string representation listing all available features to use in
    an exception message."""
    msg = ""
    for category, features_names in features_by_category.items():
        msg += f"\n\n{Colors.blue(category.title())}:"
        for feature_name in features_names:
            feature = all_features[feature_name.lower()]
            docstring = getattr(feature, "__doc__", "")
            msg += f"\n{Colors.red(' * ')}{Colors.blue(feature_name)}"
            if docstring:
                msg += f"{Colors.red(' - '+feature.__doc__)}"
    return msg


def get_feature(name_feature: str) -> Type:
    """Get the function associated with the given feature name

    :param name_feature: Name of the feature

    :returns: class that implements the given feature
    :raises: InvalidArgument
    """
    try:
        feature_class = all_features[name_feature.lower()]
    except KeyError as err:
        features_string = get_string_all_features()
        if features_string:
            msg = f"No feature {name_feature}. Choose one of the following "
            msg += "features:\n"
            msg += features_string
        else:
            msg = "No features were found, please make sure that the plugin "
            msg += "that provides the requested feature is added."
        raise InvalidArgument(msg) from err
    return feature_class()


class FeatureDefinition:
    """Flag that indicates that the class is meant to define a Cibyl
    feature.
    """


class FeatureTemplate(ABC):
    """Skeleton for a generic feature, this is meant to provide a few helpful
    methods to write features. If the query method of this class will be used,
    the get_method_to_query and get_template_args should be implemented, if not
    the feature class must implement a query method that calls a source to
    obtain information and returns the collection of models that the source
    reports."""
    method_to_query = ""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_method_to_query(self):
        """Get the source method that will be called to obtain the information
        that defines the feature."""
        pass

    @abstractmethod
    def get_template_args(self):
        """Get the arguments necessary to obtain the information that defines
        the feature."""
        pass

    def query(self, system: System, **kwargs) -> Union[dict, None]:
        """Execute the sources query that would provide the information that
        defines the feature."""
        debug = kwargs.get("debug", False)
        args = self.get_template_args()
        args.update(system.export_attributes_to_source())
        args.update(kwargs)
        try:
            source_methods = select_source_method(system,
                                                  self.get_method_to_query(),
                                                  **kwargs)
        except NoSupportedSourcesFound as exception:
            # if no sources are found in the system for this
            # particular query, jump to the next one without
            # stopping execution
            LOG.error(exception, exc_info=debug)
            return
        query_result = {}
        for source_method, _ in source_methods:
            try:
                source_obj = get_source_instance_from_method(source_method)
                source_obj.ensure_source_setup()
                query_result = source_method(**args)
                system.register_query()
                return query_result
            except SourceException as exception:
                source_info = source_information_from_method(
                        source_method)
                LOG.error("Error in %s with system %s. %s",
                          source_info, system.name.value,
                          exception, exc_info=debug)
        msg = f"Feature {self.name} could not query any source for system "
        msg += f"{system.name.value}"
        LOG.warning(msg)
        # use a return value of None to mark that no query was performed
        return
