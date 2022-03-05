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

from cibyl.cli.argument import Argument

LOG = logging.getLogger(__name__)


class CustomAction(argparse.Action):
    """Custom argparse.Action that allows in addition, to specify
    whether an argument data is populated, the function associated
    with the argument and the level in the models.
    """
    def __init__(self, *args, func=None, populated=False, level=-1, **kwargs):
        """
        argparse custom action.
        :param func: the function the argument is associated with
        """
        self.func = func
        self.level = level
        self.populated = populated
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, Argument(
            name=self.dest, description=self.help, arg_type=self.type,
            nargs=self.nargs, level=self.level, func=self.func,
            populated=self.populated,
            value=values))


class Parser:
    """This is a conceptual class representation of an app parser.
    The parser created as basic argparse based parser and later it's
    extended with arguments collected from the different CI models'
    attributes.
    """

    def __init__(self, ci_args: dict = None, app_args: dict = None):
        self.ci_args = ci_args
        if not ci_args:
            self.ci_args = {}
        self.app_args = app_args
        if not app_args:
            self.app_args = {}
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

    def parse(self, arguments=None):
        """Parses app_arguments

        :return: application general arguments (config, debug) and models'
                 arguments (jobs, systems, etc.)
        :rtype: dictionary (both)
        """
        # First item is the namespace of the parsed known arguments (we ignore
        # the arguments we are not familiar with)
        known_arguments = self.argument_parser.parse_known_args(arguments)[0]
        # Keep only the used arguments
        ci_arguments = {arg_name: arg_value for arg_name, arg_value in vars(
            known_arguments).items() if isinstance(arg_value, Argument)}
        app_arguments = {arg_name: arg_value for arg_name, arg_value in vars(
            known_arguments).items() if arg_value and not isinstance(
                arg_value, Argument)}
        return app_arguments, ci_arguments

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

    def extend(self, arguments: list, group_name: str, level: int = 0):
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
                    help=arg.description, nargs=arg.nargs,
                    action=CustomAction, func=arg.func,
                    populated=arg.populated,
                    level=level)
        except argparse.ArgumentError:
            LOG.debug("argument already exists: %s...ignoring", arg.name)
