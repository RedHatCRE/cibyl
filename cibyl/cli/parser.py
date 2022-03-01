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
import argparse
import logging

LOG = logging.getLogger(__name__)


class Parser:
    """This is a conceptual class representation of an app parser.
    The parser created as basic argparse based parser and later it's
    extended with arguments collected from the different CI models'
    attributes.
    """

    def __init__(self):
        self.argument_parser = argparse.ArgumentParser()
        self.__add_arguments()

    def __add_arguments(self) -> None:
        """Creates argparse parser with all its sub-parsers."""
        self.argument_parser.add_argument(
            '--debug', '-d', action='store_true',
            dest="debug", help='turn on debug')
        self.argument_parser.add_argument(
            '--config', '-c', dest="config_file_path")
        self.argument_parser.add_argument(
            '--plugin', '-p', dest="plugin", default="openstack")

    def parse(self):
        """Parses arguments"""
        # First item is the namespace of the parsed known arguments
        return self.argument_parser.parse_known_args()[0]

    def get_group(self, group_name: str):
        """Returns the argument parser group based on a given group_name

        :param group_name: The name of the group
        :type group_name: str

        :return: An argparse argument group if it exists and matches
                 the given group name, otherwise returns None
        :rtype: argparse._ArgumentGroup
        """
        # pylint: disable=protected-access
        # Access the private member '_action_groups' to check
        # whether the group exists
        for action_group in self.argument_parser._action_groups:
            if action_group.title == group_name:
                return action_group
        return None

    def extend(self, arguments: list, group_name: str):
        """Adds arguments to a specific argument parser group.

        :param arguments: A list of argument objects
        :type arguments: list[argument]
        :param group_name: The name of the argument parser group
        :type group_name: str
        """
        group = self.get_group(group_name)
        # If the group doesn't exists, we would like to add it
        # so arguments are grouped based on the model class they belong to
        if not group:
            group = self.argument_parser.add_argument_group(group_name)

        try:
            for arg in arguments:
                group.add_argument(
                    arg.name, type=arg.arg_type,
                    help=arg.description, nargs=arg.nargs)
        except argparse.ArgumentError:
            LOG.debug("argument already exists: %s...ignoring", arg.name)
