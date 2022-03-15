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

from cibyl.cli.parser import Parser
from cibyl.config import Config
from cibyl.exceptions.config import InvalidConfiguration
from cibyl.exceptions.source import NoValidSources
from cibyl.models.ci.environment import Environment
from cibyl.publisher import Publisher
from cibyl.sources.source import Source

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

    def load_configuration(self):
        """Loads the configuration of the application."""
        self.config.load()

    def create_ci_environments(self) -> None:
        """Creates CI environment entities based on loaded configuration."""
        try:
            for env_name, systems_dict in \
                    self.config.data.get('environments', {}).items():
                environment = Environment(name=env_name)
                for system_name, single_system in systems_dict.items():
                    sources_dict = single_system.pop('sources', {})
                    sources = [Source.get_source_class(
                            source_data.get('driver'))(
                                name=source_name, **source_data)
                        for source_name, source_data in sources_dict.items()]
                    environment.add_system(name=system_name,
                                           **single_system, sources=sources)
                self.environments.append(environment)
        except AttributeError as exception:
            raise InvalidConfiguration from exception

    @staticmethod
    def populate(environment, model_instances):
        """Populate environment instance with the provided model instances"""
        for model_instance in model_instances:
            LOG.debug("populating environment %s: %s",
                      environment, model_instance)

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
        return Source.get_source_method(system.name.value, system_sources,
                                        argument.func)

    def run_query(self, start_level=1):
        """Execute query based on provided arguments."""
        last_level = -1
        for arg in sorted(self.parser.ci_args.values(),
                          key=operator.attrgetter('level'), reverse=True):
            if arg.level >= start_level and arg.level >= last_level:
                if not arg.func:
                    # if an argument does not have a function
                    # associated, we should not consider it here, e.g.
                    # --sources
                    continue
                for env in self.environments:
                    for system in env.systems:
                        source_method = self.select_source_method(system, arg)
                        model_instances_dict = source_method(
                            **self.parser.ci_args)
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
