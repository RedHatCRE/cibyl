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
import operator
import re
import time
from copy import deepcopy
from typing import List, Optional

import cibyl.exceptions.config as conf_exc
from cibyl.cli.argument import Argument
from cibyl.cli.parser import Parser
from cibyl.cli.query import get_query_type
from cibyl.cli.validator import Validator
from cibyl.config import AppConfig
from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.source import NoSupportedSourcesFound, SourceException
from cibyl.features import get_feature, get_string_all_features, load_features
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.models.ci.system_factory import SystemType
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.models.product.feature import Feature
from cibyl.publisher import Publisher
from cibyl.sources.source import (Source, get_source_instance_from_method,
                                  select_source_method,
                                  source_information_from_method)
from cibyl.sources.source_factory import SourceFactory
from cibyl.utils.dicts import intersect_models
from cibyl.utils.status_bar import StatusBar

LOG = logging.getLogger(__name__)


class Orchestrator:
    """This is a conceptual class representation of an app orchestrator.
    The purpose of the orchestrator is to run and coordinate the different
    phases of the application's lifecycle:

        1. Create initial parser
        2. Load the configuration
        3. Create the CI entities
        4. Update parser based on CI entities arguments
        5. Run query
        6. Print results
    """

    def __init__(self, environments: list = None):
        """Orchestrator constructor method"""
        self.parser = Parser()
        self.config = AppConfig()
        self.publisher = Publisher()
        if not environments:
            self.environments = []

    def get_source(self, source_name: str, source_data: dict) -> Source:
        try:
            return SourceFactory.create_source(
                    source_data.get('driver'),
                    source_name,
                    **source_data)
        except AttributeError as exception:
            raise conf_exc.InvalidSourceConfiguration(
                source_name, source_data) from exception

    def add_system_to_environment(self, environment: Environment,
                                  system_name: str, sources: List[dict],
                                  single_system: dict) -> None:
        try:
            environment.add_system(
                name=system_name,
                sources=sources,
                **single_system
            )
        except TypeError as ex:
            re_result = re.search(r'unexpected keyword argument (.*)',
                                  ex.args[0])
            if re_result:
                raise conf_exc.NonSupportedSystemKey(
                    system_name, re_result.group(1))
            re_missing_arg = re.search(r'required positional argument: (.*)',
                                       ex.args[0])
            if re_missing_arg:
                raise conf_exc.MissingSystemKey(
                    system_name, re_missing_arg.group(1))
            raise

    def create_ci_environments(self) -> None:
        """Creates CI environment entities based on loaded configuration."""
        for env_name, systems_dict in self.config.environments.items():
            enabled = systems_dict.get('enabled', True)
            if not enabled:
                continue
            environment = Environment(name=env_name, enabled=enabled)

            for system_name, single_system in systems_dict.items():
                sources_dict = single_system.pop('sources', {})
                sources = []
                for source_name, source_data in sources_dict.items():
                    sources.append(
                        self.get_source(source_name, source_data))

                self.add_system_to_environment(environment, system_name,
                                               sources, single_system)

            self.environments.append(environment)
        self.set_system_api()

    def set_system_api(self) -> None:
        """Modify the System API depending on the type of systems present in
        the configuration."""
        zuul_system_present = False
        for env in self.environments:
            for system in env.systems:
                if system.system_type.value == SystemType.ZUUL:
                    zuul_system_present = True
        if zuul_system_present:
            System.API = deepcopy(ZuulSystem.API)
        else:
            System.API = deepcopy(JobsSystem.API)

    def validate_environments(self) -> None:
        """Validate and filter environments created from configuration file
        according to user input."""
        # we keep only the environments consistent with the user input, this
        # should be helpful for the publisher to avoid showing unnecessary
        # information
        validator = Validator(self.parser.ci_args)
        self.environments = validator.validate_environments(self.environments)

    def load_features(self) -> list:
        """Read user-requested features and setup the right argument to query
        the information for them."""
        user_features = self.parser.ci_args.get('features')
        if user_features is None:
            return []
        load_features()
        if not user_features.value:
            # throw error in case cibyl is called with --features argument but
            # without any specified feature
            features_string = get_string_all_features()
            if features_string:
                msg = "No feature specified. Choose one of the following "
                msg += "features:"
                msg += features_string
            else:
                msg = "No features were found, please make sure that the "
                msg += "plugin that provides the requested feature is added."
            raise InvalidArgument(msg)
        return [get_feature(feature_name)
                for feature_name in user_features.value]

    def run_features(self, system: System, features_to_run: list) -> None:
        """Run user-requested features, the output of each feature will be
        stored in the system attributes. This output can either be
        whether the feature is tested in the system or jobs where the feature
        is tested."""
        features_combination = None

        with StatusBar(f"Fetching features ({system.name})"):
            for feature_to_run in features_to_run:
                feature_info = feature_to_run.query(system,
                                                    **self.parser.ci_args,
                                                    **self.parser.app_args)
                if feature_info is None:
                    # no successful query was performed
                    system.add_feature(Feature(feature_to_run.name,
                                               "N/A"))
                    # set the returned info to an empty container
                    # to have an empty intersection
                    feature_info = AttributeDictValue("name")
                else:
                    system.add_feature(Feature(feature_to_run.name,
                                               bool(feature_info)))

                if "jobs" in self.parser.ci_args:
                    if features_combination is None:
                        features_combination = feature_info
                    else:
                        features_combination = intersect_models(
                                features_combination, feature_info)

        if "jobs" in self.parser.ci_args:
            # add the combined result for all features requested, e.g.
            # the jobs that match all the features
            system.populate(features_combination)

    def sort_and_filter_args(self) -> List[Argument]:
        """Get a list of arguments that provide the queries that the sources
        should perform. This requires filtering out the argument that have no
        func associated, sorting the arguments by level and then making sure
        that only one of the arguments is kept if many point to the same query
        (e.g --builds and --build-status).
        :returns: List of arguments that contain queries for the sources
        """
        args_with_query = {name: arg for name, arg in
                           self.parser.ci_args.items() if arg.func}
        sorted_args = sorted(args_with_query.values(),
                             key=operator.attrgetter('level'), reverse=True)
        queries = set()
        final_args_to_query = []
        for arg in sorted_args:
            if arg.func not in queries:
                queries.add(arg.func)
                final_args_to_query.append(arg)
        return final_args_to_query

    def run_query(self, system: System, start_level: int = 1) -> None:
        """Execute query based on provided arguments."""
        if not system.is_enabled():
            return
        debug = self.parser.app_args.get("debug", False)
        # sort cli arguments in decreasing order by level
        sorted_args = self.sort_and_filter_args()
        # collect system-level arguments that can affect the
        # result of the source method call
        system_args = system.export_attributes_to_source()
        ci_args = self.parser.ci_args
        query_result = None
        last_level = -1
        for arg in sorted_args:
            if arg.level >= start_level and arg.level >= last_level:
                # we update last_level if the the arg has a func attribute
                # and valid sources to query
                last_level = arg.level
                try:
                    source_methods = select_source_method(system, arg.func,
                                                          **ci_args)
                except NoSupportedSourcesFound as exception:
                    # if no sources are found in the system for this
                    # particular query, jump to the next one without
                    # stopping execution
                    LOG.error(exception, exc_info=debug)
                    continue
                for source_method, speed_score in source_methods:
                    source_info = source_information_from_method(
                            source_method)
                    source_obj = get_source_instance_from_method(source_method)
                    source_obj.ensure_source_setup()
                    start_time = time.time()
                    LOG.info("Performing query on system %s", system.name)
                    LOG.debug("Running %s and speed index %d",
                              source_info, speed_score)
                    try:
                        with StatusBar(f"Performing query ({system.name})"):
                            model_instances_dict = source_method(
                                **ci_args, **self.parser.app_args,
                                **system_args)
                    except SourceException as exception:
                        LOG.error("Error in %s under system: '%s'. "
                                  "Reason: '%s'.",
                                  source_info, system.name.value,
                                  exception, exc_info=debug)
                        continue
                    if query_result is None:
                        query_result = model_instances_dict
                    else:
                        query_result = intersect_models(query_result,
                                                        model_instances_dict)
                    end_time = time.time()
                    LOG.info("Took %.2fs to query system %s using %s",
                             end_time-start_time, system.name.value,
                             source_info)
                    system.register_query()
                    # if one source has provided the information, there is
                    # no need to query the rest
                    break
        if query_result:
            # if no source could be called, there is nothing to add
            system.populate(query_result)

    def extend_parser(self, attributes: dict, group_name: str = 'Environment',
                      level: int = 0) -> None:
        """Extend parser with arguments from CI models."""
        for attr_dict in attributes.values():
            arguments = attr_dict.get('arguments')
            class_type = attr_dict.get('attr_type')
            has_api = class_type not in [str, list, dict, int] and \
                hasattr(class_type, 'API')
            if has_api:
                # API entry is related to a model that has an API
                new_group_name = class_type.__name__
                if arguments:
                    # add the arguments found in the current entry, but relate
                    # them to the model
                    self.parser.extend(arguments, new_group_name,
                                       level=level+1)
                # explore the API of the model found, even if there are no
                # arguments
                self.extend_parser(class_type.API, new_group_name,
                                   level=level+1)
            elif arguments:
                # if the API entry has arguments but is not related to any
                # model, just add them
                self.parser.extend(arguments, group_name, level=level)

    def query_and_publish(self, output_style: str = "colorized",
                          features: Optional[list] = None) -> None:
        """Iterate over the environments and their systems and publish
        the results of the queries.

        The query is performed per system, while the results are published
        once per environment"""
        for env in self.environments:
            for system in env.systems:
                if features:
                    self.run_features(system, features)
                else:
                    self.run_query(system)
                for source in system.sources:
                    source.ensure_teardown()
            self.publisher.publish(
                environment=env,
                style=output_style,
                query=get_query_type(**self.parser.ci_args),
                verbosity=self.parser.app_args.get('verbosity'),
                complete=self.parser.app_args.get('complete', None))
