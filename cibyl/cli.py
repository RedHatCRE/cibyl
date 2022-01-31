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
from cibyl.value import ValueInterface
from cibyl.value import ListValue

LOG = logging.getLogger(__name__)


def create_parser(entities) -> argparse.ArgumentParser:
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
    query_parser = add_query_parser(subparsers)
    populate_query_parser(query_parser, entities)

    return parser


def add_query_parser(subparsers) -> None:
    """Creates the sub-parser 'query'."""
    query_parser = subparsers.add_parser("query")
    query_parser.set_defaults(func=query)
    query_parser.add_argument('--debug', '-d', action='store_true',
                              dest="debug", help='turn on debug')
    query_parser.add_argument('--config', dest="config_file_path",
                              default=Config.DEFAULT_FILE_PATH)
    return query_parser


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
    if 'environments' in config:
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


def get_parser_group(parser, group_name):
    group = None
    for action_group in parser._action_groups:
        if action_group.title == group_name:
            group = action_group
    if not group:
        group = parser.add_argument_group(group_name)
    return group


def add_arguments(parser, attributes, group_name):
    for attr_name, value in attributes.items():
        group = get_parser_group(parser, group_name)
        if isinstance(value, ValueInterface):
            try:
                group.add_argument(value.arg_name, type=value.type)
            except argparse.ArgumentError:
                LOG.debug("ignoring duplicate argument: {}".format(
                    value.arg_name))
            try:
                if isinstance(value, ListValue):
                    for item in value.data:
                        add_arguments(parser, vars(item),
                                      item.__class__.__name__)
                else:
                    add_arguments(parser, vars(value.data),
                                  value.type.__class__.__name__)
            except TypeError:
                pass


def populate_query_parser(query_parser, entities) -> None:
    for entity in entities:
        add_arguments(query_parser, vars(entity),
                      group_name=entity.__class__.__name__)


def query(entities):
    output(entities)


def output(entities):
    for entity in entities:
        print(entity)


def mark_attributes_to_populate(args, attributes):
    for attr_name, value in attributes.items():
        if attr_name in args and args[attr_name]:
            value.populate = True
        if isinstance(value, ValueInterface):
            try:
                if isinstance(value, ListValue):
                    for item in value.data:
                        mark_attributes_to_populate(args, vars(item))
                else:
                    mark_attributes_to_populate(args, vars(value.data))
            except TypeError:
                pass


def main():
    config_file_path = Config.DEFAULT_FILE_PATH
    for i, item in enumerate(sys.argv[1:]):
        if item == "--config":
            config_file_path = sys.argv[i+2]

    config = Config(file_path=config_file_path)
    config.load()
    entities = generate_entities(config.data)
    parser = create_parser(entities)
    args = parser.parse_args()
    setup_logging(args.debug)

    for entity in entities:
        mark_attributes_to_populate(vars(args), vars(entity))

    if hasattr(args, 'func'):
        args.func(entities)
    else:
        LOG.info("usage: {}".format(crayons.yellow("cibyl query")))


if __name__ == '__main__':
    sys.exit(main())
