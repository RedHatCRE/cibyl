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
from typing import Callable, List, Optional, Set

import networkx as nx

from cibyl.cli.argument import Argument

LOG = logging.getLogger(__name__)


class CustomAction(argparse.Action):
    """Custom argparse.Action that allows in addition, to specify
    whether an argument data is populated, the function associated
    with the argument and the level in the models.
    """
    def __init__(self, *args, func: Callable = None, populated: bool = False,
                 level: int = -1, ranged: bool = False, **kwargs):
        """
        argparse custom action.
        :param func: the function the argument is associated with
        """
        self.func = func
        self.level = level
        self.populated = populated
        self.ranged = ranged
        super().__init__(*args, **kwargs)

    def __call__(self, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: List[str],
                 option_string: str = None):
        if self.default and not values:
            values = self.default
        setattr(namespace, self.dest, Argument(
            name=self.dest, description=self.help, arg_type=self.type,
            nargs=self.nargs, level=self.level, func=self.func,
            ranged=self.ranged, populated=self.populated, value=values))


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
        # parser for model-related arguments
        self.model_parser = argparse.ArgumentParser(add_help=False)
        # application-wide parser that will contain all the subparsers
        self.app_parser = argparse.ArgumentParser()

        self.__add_arguments()
        self.graph_queries = nx.DiGraph()

    def __add_arguments(self) -> None:
        """Creates argparse parser with all its sub-parsers."""
        general_args_title = "General cibyl options"
        app_args_group = self.app_parser.add_argument_group(general_args_title)
        app_args_group.add_argument(
            '--debug', '-d', action='store_true',
            dest="debug", help='turn on debug')
        app_args_group.add_argument(
            '--config', '-c', dest="config_file_path")
        app_args_group.add_argument(
            '--log-file', dest="log_file",
            help='Path to store the output, default is cibyl_output.log')
        app_args_group.add_argument(
            '--log-mode', dest="log_mode",
            choices=("terminal", "file", "both"),
            help='Where to write the output, default is both')
        app_args_group.add_argument(
            '--output', '-o', dest='output_file_path',
            help='Write output into <OUTPUT_FILE_PATH>.'
        )
        app_args_group.add_argument(
            '--output-format', '-f', choices=("text", "colorized", "json"),
            dest="output_style", default="colorized",
            help="Sets the output format."
        )
        app_args_group.add_argument(
            '--plugin', '-p', dest="plugin", default="openstack")
        app_args_group.add_argument(
            '-v', '--verbose', dest="verbosity", default=0, action="count",
            help="Causes Cibyl to print more debug messages. "
                 "Adding multiple -v will increase the verbosity.")

    def add_subparsers(self, subparser_creators: List[Callable] = []) -> None:
        """Add subparsers to the application-wide argument parser."""
        subparsers_title = "Available subcommands"
        subparsers = self.app_parser.add_subparsers(dest="command",
                                                    title=subparsers_title)
        # subparser for normal queries
        subparsers.add_parser("query", add_help=True,
                              parents=[self.model_parser])
        # subparser for features
        features_sp = subparsers.add_parser("features", add_help=True)
        features_sp.add_argument("features", nargs="*",
                                 help="Features to query")
        features_sp.add_argument("--jobs", type=str, nargs='*',
                                 func='get_jobs', action=CustomAction,
                                 help="List jobs that use the features")
        for function in subparser_creators:
            function(subparsers)

    def print_help(self) -> None:
        """Call argparse's print_help method to show the help message with the
        arguments that are currently added."""
        self.app_parser.print_help()

    def add_argument_to_tree(self, arg: Argument,
                             parent_queries: Set[str]) -> None:
        """Add argument to the tree of query method relationships. This tree
        relates query method that have dependencies, e.g. get_jobs and
        get_builds. Queries are added as nodes and the edges of the graph marks
        the relationships. Nodes cannot be duplicated and self-links are
        avoided."""
        self.graph_queries.add_node(arg.func)
        for query in parent_queries:
            if query == arg.func:
                # avoid creating self-links
                continue
            # the add_node and add_edge functions from the networkx are
            # idempotent, if we add the same node twice, nothing happens in the
            # second occurrence
            self.graph_queries.add_node(query)
            self.graph_queries.add_edge(query, arg.func)

    def parse(self, arguments: List[Argument] = None) -> None:
        """Parse application and CI models arguments.

        Sets the attributes ci_args and app_args with dictionaries
        including the parsed arguments.

        :param arguments: Arguments to parse
        """

        arguments = vars(self.app_parser.parse_args(arguments))
        # Keep only the used arguments
        self.ci_args = {arg_name: arg_value for arg_name, arg_value in
                        arguments.items() if isinstance(arg_value, Argument)}
        self.app_args = {arg_name: arg_value for arg_name, arg_value in
                         arguments.items() if arg_value is not None and not
                         isinstance(arg_value, Argument)}

    def get_group(self, group_name: str) -> Optional[argparse._ArgumentGroup]:
        """Returns the argument parser group based on a given group_name

        :param group_name: The name of the group

        :return: An argparse argument group if it exists and matches the
        given group name, otherwise returns None
        """
        # pylint: disable=protected-access
        # Access the private member '_action_groups' to check
        # whether the group exists
        for action_group in self.model_parser._action_groups:
            if action_group.title == group_name:
                return action_group
        return None

    def extend(self, arguments: List[Argument], group_name: str,
               level: int = 0,
               parent_queries: Optional[Set[str]] = None) -> None:
        """Adds arguments to a specific argument parser group.

        :param arguments: A list of argument objects
        :param group_name: The name of the argument parser group
        :param level: The level of the arguments in models
        :param parent_queries: The query methods of the source that comes
        before the ones in the arguments to add
        """
        group = self.get_group(group_name)
        # If the group doesn't exists, we would like to add it
        # so arguments are grouped based on the model class they belong to
        if not group:
            group = self.model_parser.add_argument_group(group_name)

        try:
            for arg in arguments:
                if parent_queries and arg.func:
                    self.add_argument_to_tree(arg, parent_queries)
                group.add_argument(
                    arg.name, type=arg.arg_type,
                    help=arg.description, nargs=arg.nargs,
                    action=CustomAction, func=arg.func,
                    ranged=arg.ranged,
                    populated=arg.populated,
                    default=arg.default,
                    level=level, choices=arg.choices)
        except argparse.ArgumentError:
            pass
