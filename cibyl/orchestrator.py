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
import crayons
import importlib
import logging
import re
import sys

from cibyl.config import Config
from cibyl.models.ci.environment import Environment
from cibyl.parser import create_parser
from cibyl.value import ValueInterface
from cibyl.value import ListValue


LOG = logging.getLogger(__name__)


class Orchestrator(object):

    def __init__(self, args=None):
        self.args = args

    def prepare(self):
        self.load_configuration()

    def run(self):
        # Generate CI environment entities based on loaded configuration
        ci_environments = self.generate_env_instances(self.config.data)
        # Populate parser based on the generated environment entities
        parser = create_parser(ci_environments, self.query)
        args = parser.parse_args()

        # Set up logging based on the chosen level by the user
        self.setup_logging(args.debug)

        # Mark attributes that needs to be populated based on
        # the arguments that user have used
        for env in ci_environments:
            self.mark_attributes_to_populate(vars(args), vars(env))

        # Extend CI environment entities based on the chosen plugin
        plugin = self.get_plugin(args.plugin)
        if plugin:
            plugin.extend(ci_environments)

        if hasattr(args, 'func'):
            # Filter out only the arguments the user has actually used
            used_args = {k: v for k, v in vars(args).items() if v is not None}
            # Populate environments based on the arguments the user has passed
            args.func(ci_environments, used_args)
        else:
            LOG.info("usage: {}".format(crayons.yellow("cibyl query")))

    def post(self):
        pass

    def load_configuration(self):
        # Since parser is created only after loading the
        # configuration, we first parse it manually from
        # the arguments provided by the user
        config_file_path = Config.get_config_file_path(self.args)
        self.config = Config(file_path=config_file_path)
        self.config.load()

    def generate_env_instances(self, config) -> list:
        entities = []
        if 'environments' in config:
            for env_name, systems in config['environments'].items():
                env_instance = Environment(name=env_name)
                for system_name, system_data in systems.items():
                    try:
                        env_instance.add_system(name=system_name,
                                                **system_data)
                    except TypeError as e:
                        non_supported_arg = re.findall(
                            r'unexpected keyword argument \'(.*)\'', str(e))[0]
                        LOG.error("configuration doesn't support: {}".format(
                            crayons.red(non_supported_arg)))
                        sys.exit(2)
                entities.append(env_instance)
        return entities

    def setup_logging(self, debug) -> None:
        """Sets up basic logging with format and level defined.

        Args:
            debug: boolean that determines with debug level should be used
        """
        format = '%(message)s'
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level, format=format)

    def query(self, environments, args):
        for env in environments:
            sources = []
            for system in env.systems:
                sources = sorted(system.sources, key=lambda src: src.priority,
                                 reverse=True)
                for source in sources:
                    source.populate(env, args)
        self.output(environments)

    def output(self, environments):
        for env in environments:
            print(env)

    def mark_attributes_to_populate(self, args, attributes):
        for attr_name, value in attributes.items():
            if attr_name in args and args[attr_name]:
                value.populate = True
            if isinstance(value, ValueInterface):
                try:
                    if isinstance(value, ListValue):
                        for item in value.data:
                            self.mark_attributes_to_populate(args, vars(item))
                    else:
                        self.mark_attributes_to_populate(args,
                                                         vars(value.data))
                except TypeError:
                    pass

    def get_plugin(self, module_name):
        """Returns a plugin class instance based on the pass module name

        Args:
            module name: A str that represents the module Name
        Returns:
            The plugin class instance whose file name matches module name
        """
        Plugin = getattr(importlib.import_module(
            "cibyl.plugins.{}".format(module_name)),
            module_name.capitalize())
        if Plugin:
            return Plugin()
