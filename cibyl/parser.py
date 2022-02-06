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
import logging

from cibyl.config import Config
from cibyl.value import ValueInterface
from cibyl.value import ListValue

LOG = logging.getLogger(__name__)


def create_parser(entities, query_func) -> argparse.ArgumentParser:
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
    parser.add_argument('--plugin', dest="plugin",
                        default="openstack")
    query_parser = add_query_parser(subparsers, query_func)
    populate_query_parser(query_parser, entities)

    return parser


def add_query_parser(subparsers, query_func) -> None:
    """Creates the sub-parser 'query'."""
    query_parser = subparsers.add_parser("query")
    query_parser.set_defaults(func=query_func)
    query_parser.add_argument('--debug', '-d', action='store_true',
                              dest="debug", help='turn on debug')
    query_parser.add_argument('--config', dest="config_file_path",
                              default=Config.DEFAULT_FILE_PATH)
    query_parser.add_argument('--plugin', dest="plugin",
                              default="openstack")
    return query_parser


def populate_query_parser(query_parser, entities) -> None:
    for entity in entities:
        add_arguments(query_parser, vars(entity),
                      group_name=entity.__class__.__name__)


def add_arguments(parser, attributes, group_name):
    for attr_name, value in attributes.items():
        group = get_parser_group(parser, group_name)
        if isinstance(value, ValueInterface):
            try:
                for arg in value.args:
                    group.add_argument(
                        arg, type=value.type,
                        help=value.description, nargs=value.nargs)
            except argparse.ArgumentError:
                LOG.debug("ignoring duplicate argument: {}".format(
                    arg))
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


def get_parser_group(parser, group_name):
    group = None
    for action_group in parser._action_groups:
        if action_group.title == group_name:
            group = action_group
    if not group:
        group = parser.add_argument_group(group_name)
    return group
