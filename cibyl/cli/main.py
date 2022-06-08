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

from cibyl.cli.output import OutputStyle
from cibyl.exceptions import CibylException
from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.config import ConfigurationNotFound
from cibyl.orchestrator import Orchestrator
from cibyl.plugins import enable_plugins
from cibyl.utils.colors import Colors
from cibyl.utils.logger import configure_logging

LOG = logging.getLogger(__name__)


def raw_parsing(arguments):
    """Returns config file path if one was passed with --config argument

    :param arguments: A list of strings representing the arguments and their
                      values, defaults to None
    :type arguments: str, optional
    """
    args = {'config_file_path': None, 'help': False,
            "log_file": "cibyl_output.log", "log_mode": "both",
            "logging": logging.INFO, "plugins": [],
            "debug": False, "output_style": "colorized"}
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
            plugins = []
            for argument in arguments[(i + 2):]:
                if argument.startswith("-"):
                    break
                plugins.append(argument)
            args["plugins"] = plugins
        elif item in ('-f', '--output-format'):
            args["output_style"] = arguments[i + 2]

    setup_output_format(args)

    return args


def setup_output_format(args):
    """Parse the OutputStyle specified by the user."""
    user_output_format = args["output_style"]
    try:
        args["output_style"] = OutputStyle.from_key(user_output_format)
    except NotImplementedError:
        msg = f'Unknown output format: {user_output_format}'
        raise InvalidArgument(msg) from None


def main():
    """CLI main entry."""
    # We parse it from sys.argv instead of argparse parser because we want
    # to run the app parser only once, after we update it with the loaded
    # arguments from the CI models based on the loaded configuration file
    arguments = raw_parsing(sys.argv)

    try:
        configure_logging(arguments.get('log_mode'),
                          arguments.get('log_file'),
                          arguments.get('logging'))
        orchestrator = Orchestrator()
        try:
            orchestrator.load_configuration(arguments.get('config_file_path'))
        except ConfigurationNotFound as ex:
            # Check if the error is to be ignored
            if not arguments.get('help', False):
                raise ex
        orchestrator.create_ci_environments()
        plugins = arguments.get('plugins')
        if not plugins:
            # if user has not specified any plugins,
            # read them from configuration
            plugins = orchestrator.config.data.get('plugins', [])
        # add plugins after the environments are created, since the environment
        # might modify some of the models APIs
        if plugins:
            enable_plugins(plugins)
        # Add arguments from CI & product models to the parser of the app
        for env in orchestrator.environments:
            orchestrator.extend_parser(attributes=env.API)
        # We can parse user's arguments only after we have loaded the
        # configuration and extended based on it the parser with arguments
        # from the CI models
        orchestrator.parser.parse()
        orchestrator.validate_environments()
        orchestrator.setup_sources()
        features = orchestrator.load_features()
        orchestrator.query_and_publish(arguments["output_style"],
                                       features=features)
    except CibylException as ex:
        if arguments["debug"]:
            raise ex

        print(Colors.red(ex.message))


if __name__ == "__main__":
    main()
