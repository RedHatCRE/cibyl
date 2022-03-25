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
import time

from cibyl.cli.parser import Parser
from cibyl.cli.validator import Validator
from cibyl.config import Config
from cibyl.exceptions.config import InvalidConfiguration
from cibyl.exceptions.source import NoValidSources
from cibyl.models.ci.environment import Environment
from cibyl.publisher import Publisher
from cibyl.sources.source import get_source_method
from cibyl.sources.source_factory import SourceFactory
from cibyl.utils.source_methods_store import SourceMethodsStore

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
    info_str = f"source {source.name} of type {source.driver} using method "
    return info_str+f"{source_method.__name__}"


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

    def __init__(self, config_file_path: str = None,
                 environments: list = None):
        """Orchestrator constructor method"""
        self.config = Config(path=config_file_path)
        self.parser = Parser()
        self.publisher = Publisher()
        if not environments:
            self.environments = []

    def load_configuration(self, skip_on_missing=False):
        """Loads the configuration of the application."""
        self.config.load(skip_on_missing)

    def create_ci_environments(self) -> None:
        """Creates CI environment entities based on loaded configuration."""
        try:
            if self.config.data:
                env_data = self.config.data.get('environments', {}).items()
            else:
                env_data = {}

            for env_name, systems_dict in env_data:
                environment = Environment(name=env_name)

                for system_name, single_system in systems_dict.items():
                    sources_dict = single_system.pop('sources', {})
                    sources = []

                    for source_name, source_data in sources_dict.items():
                        sources.append(
                            SourceFactory.create_source(
                                source_data.get('driver'),
                                source_name,
                                **source_data
                            )
                        )

                    environment.add_system(
                        name=system_name,
                        sources=sources,
                        **single_system
                    )

                self.environments.append(environment)
        except AttributeError as exception:
            raise InvalidConfiguration from exception

    def select_source_method(self, system, argument):
        """Select the apropiate source considering the user input.

        :param system: system to select sources from
        :type system: :class:`.System`
        :param argument: argument that is considered for the query
        :type argument: :class:`.Argument`

        :returns: method to call from the selected source
        :rtype: function
        """
        sources_user = self.parser.ci_args.get("sources")
        system_sources = system.sources
        if sources_user:
            system_sources = [source for source in system.sources if
                              source.name in sources_user.value]
        if not system_sources:
            raise NoValidSources(system)
        return get_source_method(system.name.value, system_sources,
                                 argument.func)

    def run_query(self, start_level=1):
        """Execute query based on provided arguments."""
        last_level = -1
        validator = Validator(self.parser.ci_args)
        source_methods_store = SourceMethodsStore()
        # we keep only the environments consistent with the user input, this
        # should be helpful for the publisher to avoid showing unnecessary
        # information
        self.environments, valid_systems = validator.validate_environments(
                self.environments)
        for arg in sorted(self.parser.ci_args.values(),
                          key=operator.attrgetter('level'), reverse=True):
            if arg.level >= start_level and arg.level >= last_level:
                if not arg.func:
                    # if an argument does not have a function
                    # associated, we should not consider it here, e.g.
                    # --sources
                    continue
                # the validation process provides a flat list of systems
                # because the environment information is not used from this
                # point forward
                for system in valid_systems:
                    source_method = self.select_source_method(system, arg)
                    if source_methods_store.has_been_called(source_method):
                        # we want to avoid repeating calls to the same source
                        # method if several argument with that method are
                        # provided
                        continue
                    source_methods_store.add_call(source_method)
                    start_time = time.time()
                    model_instances_dict = source_method(
                        **self.parser.ci_args, **self.parser.app_args)
                    end_time = time.time()
                    LOG.info("Took %.2fs to query system %s using %s",
                             end_time-start_time, system.name.value,
                             source_information_from_method(source_method))
                    system.populate(model_instances_dict)
            last_level = arg.level

    def extend_parser(self, attributes, group_name='Environment',
                      level=0):
        """Extend parser with arguments from CI models."""
        for attr_dict in attributes.values():
            arguments = attr_dict.get('arguments')
            if arguments:
                self.parser.extend(arguments, group_name, level=level)
                class_type = attr_dict.get('attr_type')
                if class_type not in [str, list, dict, int] and \
                   hasattr(class_type, 'API'):
                    self.extend_parser(class_type.API, class_type.__name__,
                                       level=level+1)
