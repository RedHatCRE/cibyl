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
from collections import defaultdict
from copy import deepcopy

import cibyl.exceptions.config as conf_exc
from cibyl.cli.parser import Parser
from cibyl.cli.query import get_query_type
from cibyl.cli.validator import Validator
from cibyl.config import Config, ConfigFactory
from cibyl.exceptions.config import NonSupportedSystemKey
from cibyl.exceptions.source import (NoSupportedSourcesFound, NoValidSources,
                                     SourceException)
from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.models.ci.system_factory import SystemType
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.publisher import Publisher
from cibyl.sources.source import get_source_method
from cibyl.sources.source_factory import SourceFactory
from cibyl.utils.source_methods_store import SourceMethodsStore
from cibyl.utils.status_bar import StatusBar

LOG = logging.getLogger(__name__)


def source_information_from_method(source_method):
    """Obtain source information from a method of a source object.

    :param source_method: Source method that is used
    :type source_method: method
    :returns: string with source information identifying the object that the
    method belongs to
    :rtype: str
    """
    source = source_method.__self__
    info_str = f"source: '{source.name}' of type: '{source.driver}'"
    if LOG.getEffectiveLevel() <= logging.DEBUG:
        info_str += f" using method {source_method.__name__}"
    return info_str


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

    :param config_file_path: the absolute path of the configuration file
    :type config_file_path: str, optional
    """

    def __init__(self, environments: list = None):
        """Orchestrator constructor method"""
        self.config = Config()
        self.parser = Parser()
        self.publisher = Publisher()
        if not environments:
            self.environments = []

    def load_configuration(self, path):
        """Loads the configuration of the application."""
        self.config = ConfigFactory.from_path(path)

    def get_source(self, source_name, source_data):
        try:
            return SourceFactory.create_source(
                    source_data.get('driver'),
                    source_name,
                    **source_data)
        except AttributeError as exception:
            raise conf_exc.InvalidSourceConfiguration(
                source_name, source_data) from exception

    def add_system_to_environment(self, environment,
                                  system_name, sources, single_system):
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
                raise NonSupportedSystemKey(system_name, re_result.group(1))

    def create_ci_environments(self) -> None:
        """Creates CI environment entities based on loaded configuration."""
        try:
            if self.config.data:
                env_data = self.config.data.get('environments', {}).items()
            else:
                env_data = {}

            for env_name, systems_dict in env_data:
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
        except (AttributeError, TypeError) as exception:
            raise conf_exc.InvalidConfiguration from exception

    def set_system_api(self):
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

    def select_source_method(self, system, argument):
        """Select the apropiate source considering the user input.

        :param system: system to select sources from
        :type system: :class:`.System`
        :param argument: argument that is considered for the query
        :type argument: :class:`.Argument`

        :returns: List of pairs with source method and its speed index sorted
        by the speed index value
        :rtype: tuple
        """
        sources_user = self.parser.ci_args.get("sources")
        system_sources = system.sources
        if sources_user:
            system_sources = [source for source in system.sources if
                              source.name in sources_user.value]
        if not system_sources:
            raise NoValidSources(system,
                                 [source.name for source in system.sources])
        return get_source_method(system.name.value, system_sources,
                                 argument.func, args=self.parser.ci_args)

    def validate_environments(self):
        """Validate and filter environments created from configuration file
        according to user input."""
        # we keep only the environments consistent with the user input, this
        # should be helpful for the publisher to avoid showing unnecessary
        # information
        validator = Validator(self.parser.ci_args)
        self.environments = validator.validate_environments(self.environments)

    def setup_sources(self):
        """Setup all enabled sources present in the environment."""
        for env in self.environments:
            if env.enabled:
                for system in env.systems:
                    for source in system.sources:
                        if source.enabled:
                            source.setup()

    def run_query(self, system, start_level=1):
        """Execute query based on provided arguments."""
        debug = self.parser.app_args.get("debug", False)
        # sort cli arguments in decreasing order by level
        sorted_args = sorted(self.parser.ci_args.values(),
                             key=operator.attrgetter('level'), reverse=True)
        system_methods_stores = defaultdict(SourceMethodsStore)
        last_level = -1
        for arg in sorted_args:
            if arg.level >= start_level and arg.level >= last_level:
                if not arg.func:
                    # if an argument does not have a function
                    # associated, we should not consider it here, e.g.
                    # --sources
                    continue
                if not system.is_enabled():
                    return
                # we update last_level if the the arg has a func attribute
                # and valid sources to query
                last_level = arg.level
                source_methods_store = system_methods_stores[system.name.value]
                # collect system-level arguments that can affect the
                # result of the source method call
                system_args = system.export_attributes_to_source()
                try:
                    source_methods = self.select_source_method(system, arg)
                except NoSupportedSourcesFound as exception:
                    # if no sources are found in the system for this
                    # particular query, jump to the next one without
                    # stopping execution
                    LOG.error(exception, exc_info=debug)
                    continue
                for source_method, speed_score in source_methods:
                    if source_methods_store.has_been_called(source_method):
                        # we want to avoid repeating calls to the same
                        # source method if several arguments with that
                        # method are provided
                        if source_methods_store.get_status(source_method):
                            # if the previous call was successful, we do
                            # not need to query the same method again
                            break
                        else:
                            # if the previous call threw an error, let's
                            # try a different source
                            continue
                    source_info = source_information_from_method(
                            source_method)
                    start_time = time.time()
                    LOG.info(f"Performing query on system {system.name}")
                    LOG.debug("Running %s and speed index %d",
                              source_info, speed_score)
                    try:
                        with StatusBar(f"Performing query ({system.name})"):
                            model_instances_dict = source_method(
                                **self.parser.ci_args, **self.parser.app_args,
                                **system_args)
                    except SourceException as exception:
                        source_methods_store.add_call(source_method, False)
                        LOG.error("Error in %s under system: '%s'. "
                                  "Reason: '%s'.",
                                  source_info, system.name.value,
                                  exception, exc_info=debug)
                        continue
                    source_methods_store.add_call(source_method, True)
                    end_time = time.time()
                    LOG.info("Took %.2fs to query system %s using %s",
                             end_time-start_time, system.name.value,
                             source_info)
                    system.populate(model_instances_dict)
                    system.register_query()
                    # if one source has provided the information, there is
                    # no need to query the rest
                    break

    def extend_parser(self, attributes, group_name='Environment',
                      level=0):
        """Extend parser with arguments from CI models."""
        for attr_dict in attributes.values():
            arguments = attr_dict.get('arguments')
            if arguments:
                class_type = attr_dict.get('attr_type')
                if class_type not in [str, list, dict, int] and \
                   hasattr(class_type, 'API'):
                    self.parser.extend(arguments, group_name, level=level+1)
                    self.extend_parser(class_type.API, class_type.__name__,
                                       level=level+1)
                else:
                    self.parser.extend(arguments, group_name, level=level)

    def query_and_publish(self, output_style="colorized"):
        """Iterate over the environments and their systems and publish
        the results of the queries.

        The query and publish is performed per system"""
        for env in self.environments:
            self.publisher.publish(
                model_instance=env,
                style=output_style,
                query=get_query_type(**self.parser.ci_args),
                verbosity=self.parser.app_args.get('verbosity'))
            for system in env.systems:
                self.run_query(system)
                self.publisher.publish(
                    model_instance=system,
                    style=output_style,
                    query=get_query_type(**self.parser.ci_args),
                    verbosity=self.parser.app_args.get('verbosity'))
