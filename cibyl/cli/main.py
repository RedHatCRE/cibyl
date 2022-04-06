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

from cibyl.exceptions import CibylException
from cibyl.exceptions.cli import InvalidArgument
from cibyl.exceptions.config import ConfigurationNotFound
from cibyl.orchestrator import Orchestrator
from cibyl.plugins import DEFAULT_PLUGIN, extend_models
from cibyl.utils.logger import configure_logging
from cibyl.cli.output import OutputStyle

LOG = logging.getLogger(__name__)


def raw_parsing(arguments):
    """Returns config file path if one was passed with --config argument

    :param arguments: A list of strings representing the arguments and their
                      values, defaults to None
    :type arguments: str, optional
    """
    args = {'config_file_path': None, 'help': False,
            "log_file": "cibyl_output.log", "log_mode": "both",
            "logging": logging.INFO, "plugins": [DEFAULT_PLUGIN],
            "debug": False, "output_style": OutputStyle.COLORED}
    for i, item in enumerate(arguments[1:]):
        if item == "--config":
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
        elif item in ('-o', '--output'):
            arg = arguments[i + 2]

            try:
                args["output_style"] = OutputStyle.from_str(arg)
            except NotImplementedError:
                raise InvalidArgument(f'Unknown format type: {arg}')

    return args


def main():
    """CLI main entry."""

    # We parse it from sys.argv instead of argparse parser because we want
    # to run the app parser only once, after we update it with the loaded
    # arguments from the CI models based on the loaded configuration file
    arguments = raw_parsing(sys.argv)
    if not arguments['debug']:
        CibylException.setup_quiet_exceptions()
    configure_logging(arguments.get('log_mode'),
                      arguments.get('log_file'),
                      arguments.get('logging'))

    plugins = arguments.get('plugins')
    if plugins:
        for plugin in plugins:
            extend_models(plugin)

    orchestrator = Orchestrator()

    try:
        orchestrator.load_configuration(arguments.get('config_file_path'))
    except ConfigurationNotFound as ex:
        # Check if the error is to be ignored
        skip = arguments.get('help', False)

        if not skip:
            raise ex

    orchestrator.create_ci_environments()
    # Add arguments from CI & product models to the parser of the app
    for env in orchestrator.environments:
        orchestrator.extend_parser(attributes=env.API)

    # We can parse user's arguments only after we have loaded the
    # configuration and extended based on it the parser with arguments
    # from the CI models
    orchestrator.parser.parse()
    orchestrator.run_query()
    orchestrator.publisher.publish(
        orchestrator.environments,
        arguments["output_style"],
        verbosity=orchestrator.parser.app_args.get('verbosity'))


if __name__ == "__main__":
    main()
