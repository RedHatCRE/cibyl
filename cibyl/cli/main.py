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
import sys

from cibyl.orchestrator import Orchestrator


def get_config_file_path(arguments):
    """Returns config file path if one was passed with --config argument

    :param arguments: A list of strings representing the arguments and their
                      values, defaults to None
    :type arguments: str, optional
    """
    config_file_path = None
    for i, item in enumerate(arguments[1:]):
        if item == "--config":
            config_file_path = arguments[i + 2]
    return config_file_path


def main():
    """CLI main entry."""

    # We parse it from sys.argv instead of argparse parser because we want
    # to run the app parser only once, after we update it with the loaded
    # arguments from the CI models based on the loaded configuration file
    config_file_path = get_config_file_path(sys.argv)

    orchestrator = Orchestrator(config_file_path)
    orchestrator.load_configuration()
    orchestrator.create_ci_environments()
    for env in orchestrator.environments:
        orchestrator.extend_parser(attributes=env.API)
    # We can parse user's arguments only after we have loaded the
    # configuration and extended based on it the parser with arguments
    # from the CI models
    orchestrator.parser.parse()
    orchestrator.run_query()
    orchestrator.publisher.publish(orchestrator.environments)


if __name__ == "__main__":
    main()
