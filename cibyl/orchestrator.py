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
from typing import List, Optional, Set

import networkx as nx

import cibyl.exceptions.config as conf_exc
from cibyl.cli.argument import Argument
from cibyl.cli.output import OutputStyle
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
from cibyl.publisher import PublisherFactory, PublisherTarget
from cibyl.sources.source import (Source, get_source_instance_from_method,
                                  select_source_method,
                                  source_information_from_method)
from cibyl.sources.source_factory import SourceFactory
from cibyl.utils.dicts import intersect_models
from cibyl.utils.fs import File
from cibyl.utils.paths import resolve_home
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
        user_features = self.parser.app_args.get('features')
        if user_features is None:
            return []
        load_features()
        if not user_features:
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
                for feature_name in user_features]

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
        """Select which arguments should be used to query the sources.

        The algorithm used filters out the arguments with no func attribute,
        then sorts the remaining ones by level. For each argument the shortest
        path to a root node in the graph of queries is constructed and all
        input arguments with func values contained in that path are
        eliminated. When all input arguments have been consumed, the remaining
        arguments in the queries list are the deepes nodes in each branch of
        the queries graph, which corresponds to the queries that should be
        made to the sources.

        :returns: List of arguments that contain the queries to make to the
        sources.
        """

        args = [arg for arg in self.parser.ci_args.values() if arg.func]
        sorted_args = sorted(args,
                             key=operator.attrgetter('level'), reverse=True)
        nodes_visited = set()
        graph = self.parser.graph_queries
        # the roots fo the graph will be those nodes that have no incoming
        # edge, and thus their in_degree is zero. Essentially, this means that
        # a root node will not have any parent method, like get_jobs for
        # JobsSystem and get_tenants for ZuulSystems
        roots = list(v for v, d in graph.in_degree() if d == 0)
        queries = []
        while sorted_args:
            arg = sorted_args.pop(0)
            if arg.func in nodes_visited:
                # if the func was found in the path for a previous argument,
                # skip it
                continue
            nodes_visited.add(arg.func)
            queries.append(arg)
            for root in roots:
                # all the nodes in the path from the argument's func to a root
                # node need not be queried
                for path_to_arg in nx.all_simple_paths(graph, source=root,
                                                       target=arg.func):
                    # handle the case where there might be more than one path
                    # between the node and the root, e.g. get_jobs has two
                    # paths to the root (get_tenants). path_to_arg is a list of
                    # the intermediate nodes (query methods) between the arg
                    # and the root node, all those query method will not need
                    # to be called, so the nodes_visited set is updated with
                    # them so the arguments can be filtered accordingly
                    nodes_visited.update(path_to_arg)

        return queries

    def run_query(self, system: System) -> None:
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
        for arg in sorted_args:
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
                try:
                    source_obj.ensure_source_setup()
                    start_time = time.time()
                    LOG.info("Performing query on system %s", system.name)
                    LOG.debug("Running %s and speed index %d",
                              source_info, speed_score)
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
                end_time = time.time()
                LOG.info("Took %.2fs to query system %s using %s",
                         end_time-start_time, system.name.value,
                         source_info)
                if query_result is None:
                    query_result = model_instances_dict
                else:
                    query_result = intersect_models(query_result,
                                                    model_instances_dict)
                system.register_query()
                # if one source has provided the information, there is
                # no need to query the rest
                break
        if query_result:
            # if no source could be called, there is nothing to add
            system.populate(query_result)

    def extend_parser(self, attributes: dict, group_name: str = 'Environment',
                      level: int = 0,
                      parent_queries: Optional[Set[str]] = None) -> None:
        """
        Extend parser with arguments from CI models.

        :param attributes: Dictionary containing the relevant attributes of
        a Model subclass, corresponds to the Model API.
        :param group_name: Name to use for the group of arguments in the
        command line help message
        :param level: Level of the arguments, it increases as a new Model API
        is explored and is used later to filter the user arguments and form
        queries for the sources
        :param parent_queries: Sources' query methods that have a dependency
        relationship with the query methods associated with the arguments
        found in the attributes dictionary
        """
        for attr_dict in attributes.values():
            arguments = attr_dict.get('arguments')
            class_type = attr_dict.get('attr_type')
            has_api = class_type not in [str, list, dict, int] and \
                hasattr(class_type, 'API')
            if has_api:
                # API entry is related to a model that has an API
                new_group_name = class_type.__name__
                next_parent_queries = parent_queries
                if arguments:
                    # add the arguments found in the current entry, but
                    # group them to the model they relate to
                    self.parser.extend(arguments, new_group_name,
                                       level=level+1,
                                       parent_queries=parent_queries)

                    # generate a set of all query method associated with
                    # the arguments
                    query_methods = {arg.func for arg in arguments
                                     if arg.func is not None}
                    if query_methods:
                        # if we found some query method in the arguments,
                        # set it up as the parent_func to use when
                        # recursing to explore the next Model's API
                        next_parent_queries = query_methods

                # explore the API of the model found, even if there are no
                # arguments
                self.extend_parser(class_type.API, new_group_name,
                                   level=level+1,
                                   parent_queries=next_parent_queries)
            elif arguments:
                # if the API entry has arguments but is not related to any
                # model, just add them
                self.parser.extend(arguments, group_name, level=level,
                                   parent_queries=parent_queries)

    def query_and_publish(self, output_path: Optional[str] = None,
                          output_style: OutputStyle = OutputStyle.COLORIZED,
                          features: Optional[list] = None) -> None:
        """Iterate over the environments and their systems and publish
        the results of the queries.

        The query is performed per system, while the results are published
        once per environment if the output format is text or colorized, but are
        published at the end of all queries for json format.

        :param output_path: Path to write the output to (if not defined print
        to stdout)
        :param output_style: Style to print the output with
        :param features: List of features to query for, it will be None for the
        'query' subcommand
        """

        def query():
            for system in env.systems:
                if command == "features":
                    self.run_features(system, features)
                else:
                    self.run_query(system)
                for source in system.sources:
                    source.ensure_teardown()

        command = self.parser.app_args.get('command')
        query_type = get_query_type(**self.parser.ci_args, command=command)

        target = PublisherTarget.TERMINAL
        file = None
        if output_path:
            target = PublisherTarget.FILE

            # Overwrite file if it already exists
            file = File(output_path, resolve_home)
            file.delete()
            file.create()

        publisher = PublisherFactory.create_publisher(
                target=target,
                style=output_style,
                query=query_type,
                verbosity=self.parser.app_args.get('verbosity', 0),
                output_file=file)

        for env in self.environments:
            query()
            publisher.publish(environment=env)
        publisher.finish_publishing()
