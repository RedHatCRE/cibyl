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
import argparse
import crayons
import logging
import re
import sys

from cibyl.config import Config
from cibyl.models.ci.environment import Environment

LOG = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Creates argparse parser with all its sub-parsers.

    Returns:
        argparse.ArgumentParser with its sub-parsers
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('--debug', '-d', action='store_true',
                        dest="debug", help='turn on debug')
    parser.add_argument('--config', dest="config_file_path",
                        default=Config.DEFAULT_FILE_PATH)
    add_query_parser(subparsers)

    return parser


def add_query_parser(subparsers) -> None:
    """Creates the sub-parser 'query'."""
    subparsers.add_parser("query")


def populate_parser(parser, entities):
    pass


def setup_logging(debug) -> None:
    """Sets up basic logging with format and level defined.

    Args:
        debug: boolean that determines with debug level should be used
    """
    format = '%(message)s'
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=format)


def generate_entities(config) -> list:
    entities = []
    for env_name, systems in config['environments'].items():
        env_instance = Environment(name=env_name)
        for system_name, system_data in systems.items():
            try:
                env_instance.add_system(name=system_name, **system_data)
            except TypeError as e:
                non_supported_arg = re.findall(
                    r'unexpected keyword argument \'(.*)\'', str(e))[0]
                LOG.error("configuration doesn't support: {}".format(
                    crayons.red(non_supported_arg)))
                sys.exit(2)
        entities.append(env_instance)
    return entities


def populate_query_parser(query_parser, entities) -> None:
    pass


def main():
    parser = create_parser()
    args = parser.parse_args()

    config = Config(file_path=args.config_file_path)
    config.load()
    entities = generate_entities(config.data)

    populate_query_parser(parser, entities)
    args = parser.parse_args()
    setup_logging(args.debug)

    for entity in entities:
        print(entity)


if __name__ == '__main__':
    sys.exit(main())
