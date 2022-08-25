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
import sys
from typing import List

from cibyl.cli.output import OutputStyle
from cibyl.exceptions import CibylException
from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.config import ConfigurationNotFound, EmptyConfiguration
from cibyl.orchestrator import Orchestrator
from cibyl.plugins import enable_plugins
from cibyl.utils.colors import Colors
from cibyl.utils.logger import configure_logging

LOG = logging.getLogger(__name__)


def get_plugins_from_arguments(arguments: List[str], index: int) -> List[str]:
    """Get the list of plugins from the arguments list. This requires iterating
    through the argument list until another argument (starting with a '-') or
    a subcommand (query, features, spec) is found.

    :param arguments: A list of strings representing the arguments and their
                      values, defaults to None
    :param index: Index of the arguments list to start looking at
    :returns: List of plugin names found in argument list
    """
    # list of all possible subcommands, needed so a command like
    # cibyl -p plugin1 query --jobs does not mistake the query subcommand with
    # a plugin name
    subcommands_list = ["query", "spec", "features"]
    plugins = []
    for argument in arguments[(index + 2):]:
        if argument.startswith("-") or argument in subcommands_list:
            break
        plugins.append(argument)

    return plugins


def raw_parsing(arguments: List[str]) -> dict:
    """Returns config file path if one was passed with --config argument

    :param arguments: A list of strings representing the arguments and their
                      values, defaults to None
    """
    args = {'config_file_path': None, 'help': False,
            "log_file": "cibyl_output.log", "log_mode": "both",
            "logging": logging.INFO, "plugins": [],
            "debug": False, "output_file_path": None,
            "output_style": "colorized"}
    for i, item in enumerate(arguments[1:]):
        if item in ('-c', '--config'):
            args['config_file_path'] = arguments[i + 2]
        if item in ('-h', '--help'):
            args['help'] = True
        if item == "--log-file":
            args["log_file"] = arguments[i + 2]
        elif item == "--log-mode":
            args["log_mode"] = arguments[i + 2]
        elif item in ('-d', '--debug'):
            args["logging"] = logging.DEBUG
            # add both arguments so that the checking code to enable the
            # exception traceback is clearer
            args["debug"] = True
        elif item in ('-p', '--plugin'):
            args["plugins"] = get_plugins_from_arguments(arguments, i)
        elif item in ('-o', '--output'):
            args["output_file_path"] = arguments[i + 2]
        elif item in ('-f', '--output-format'):
            args["output_style"] = arguments[i + 2]

    setup_output_format(args)

    return args


def setup_output_format(args: dict) -> None:
    """Parse the OutputStyle specified by the user."""
    user_output_format = args["output_style"]
    try:
        args["output_style"] = OutputStyle.from_key(user_output_format)
    except NotImplementedError:
        msg = f'Unknown output format: {user_output_format}'
        raise InvalidArgument(msg) from None


def main() -> None:
    """CLI main entry."""
    # We parse it from sys.argv instead of argparse parser because we want
    # to run the app parser only once, after we update it with the loaded
    # arguments from the CI models based on the loaded configuration file
    arguments = raw_parsing(sys.argv)
    configure_logging(arguments.get('log_mode'),
                      arguments.get('log_file'),
                      arguments.get('logging'))
    orchestrator = Orchestrator()

    try:
        try:
            orchestrator.config.load(path=arguments.get('config_file_path'))
            orchestrator.config.verify()
        except (ConfigurationNotFound, EmptyConfiguration) as ex:
            # Check if the error is to be ignored
            if not arguments.get('help', False):
                raise ex
        orchestrator.create_ci_environments()
        plugins = arguments.get('plugins')
        if not plugins:
            # if user has not specified any plugins,
            # read them from configuration
            plugins = orchestrator.config.plugins
        # add plugins after the environments are created, since the environment
        # might modify some of the models APIs
        plugin_parsers = []
        if plugins:
            plugin_parsers = enable_plugins(plugins)
        # Add arguments from CI & product models to the parser of the app
        for env in orchestrator.environments:
            orchestrator.extend_parser(attributes=env.API)
        orchestrator.parser.add_subparsers(subparser_creators=plugin_parsers)
        # We can parse user's arguments only after we have loaded the
        # configuration and extended based on it the parser with arguments
        # from the CI models
        orchestrator.parser.parse()
        orchestrator.validate_environments()
        features = orchestrator.load_features()
        orchestrator.query_and_publish(
            output_path=arguments["output_file_path"],
            output_style=arguments["output_style"],
            features=features
        )
    except CibylException as ex:
        if arguments.get('help', False):
            # if the user wants to see the --help, we should show it even if
            # there was some exception raised, e.g. empty or not found
            # configuration, missing environments, systems, etc.
            orchestrator.parser.print_help()
            sys.exit(1)

        if arguments["debug"]:
            raise ex

        print(Colors.red(ex.message))


if __name__ == "__main__":
    main()
