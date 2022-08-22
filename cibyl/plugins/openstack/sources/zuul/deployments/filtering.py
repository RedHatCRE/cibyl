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
import functools
from typing import Callable, Dict, Iterable

from cibyl.cli.argument import Argument
from cibyl.cli.ranged_argument import RANGE_OPERATORS, Range
from cibyl.models.attribute import AttributeValue
from cibyl.models.model import Model
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.utils.filtering import matches_regex

Arguments = Dict[str, Argument]
"""Structure where the input arguments are stored in."""

Pattern = str
"""Regex pattern to filter by."""
Check = Callable[[Deployment, Pattern], bool]
"""Test that a filter performs."""
Filter = Callable[[Deployment], bool]
"""Type of filters stored in this class."""


class DeploymentFiltering:
    """Takes care of applying the filters coming from the command line to a
    deployment.
    """

    def __init__(self, filters=None):
        """Constructor.

        :param filters: Collection of filters that will be applied to
            deployments.
        :type filters: list[:class:`DeploymentFiltering.Filter`]
        """
        if not filters:
            filters = []

        self._filters = filters

    @property
    def filters(self) -> Iterable[Filter]:
        """
        :return: Collection of filters hold by this.
        """
        return self._filters

    def add_filters_from(self, **kwargs):
        """Generates and adds to this filters coming from the command line
        arguments. The arguments are interpreted, the filters generated from
        them and then appended to the list of filters already present here.

        :param kwargs: The command line arguments.
        """
        self._handle_simple_args(**kwargs)
        self._handle_dict_args(**kwargs)
        self._handle_ranged_args(**kwargs)

    def _handle_simple_args(self, **kwargs):
        deployment_args = (
            'release',
            'infra_type',
            'topology'
        )

        for arg in deployment_args:
            self._handle_filter_for_simple_arg(
                arg,
                kwargs,
                lambda dpl: dpl
            )

        network_args = (
            'network_backend',
            'ip_version',
            'ml2_driver'
        )

        for arg in network_args:
            self._handle_filter_for_simple_arg(
                arg,
                kwargs,
                lambda dpl: dpl.network.value
            )

        storage_args = (
            'cinder_backend',
        )

        for arg in storage_args:
            self._handle_filter_for_simple_arg(
                arg,
                kwargs,
                lambda dpl: dpl.storage.value
            )

    def _handle_dict_args(self, **kwargs):
        deployment_args = (
            'nodes',
        )

        for arg in deployment_args:
            self._handle_filter_for_dict_arg(
                arg,
                kwargs,
                lambda dpl: dpl,
                lambda mdl: mdl.name
            )

    def _handle_ranged_args(self, **kwargs):
        # Argument -> Role
        nodes_args = {
            'controllers': 'controller'
        }

        for arg, role in nodes_args.items():
            self._handle_filter_for_nodes_arg(
                arg,
                role,
                kwargs,
                lambda dpl: dpl.nodes.value.values()
            )

    def _handle_filter_for_simple_arg(
        self,
        arg: str,
        args: Arguments,
        get_model: Callable[[Deployment], Model]
    ):
        for pttrn in self._get_patterns(arg, args):
            self._add_filter_for_simple_arg(arg, pttrn, get_model)

    def _handle_filter_for_dict_arg(
        self,
        arg: str,
        args: Arguments,
        get_model: Callable[[Deployment], Model],
        get_attr: Callable[[Model], AttributeValue]
    ):
        for pttrn in self._get_patterns(arg, args):
            self._add_filter_for_dict_arg(arg, pttrn, get_model, get_attr)

    def _get_patterns(self, arg: str, args: Arguments) -> Iterable[Pattern]:
        if arg not in args:
            return ()

        return args[arg].value

    def _handle_filter_for_nodes_arg(
        self,
        arg: str,
        role: str,
        args: Arguments,
        get_nodes: Callable[[Deployment], Iterable[Node]]
    ):
        for rng in self._get_ranges(arg, args):
            self._add_filter_for_nodes_arg(role, rng, get_nodes)

    def _get_ranges(self, arg: str, args: Arguments) -> Iterable[Range]:
        if arg not in args:
            return ()

        return args[arg].value

    def _add_filter_for_simple_arg(
        self,
        arg: str,
        pattern: Pattern,
        get_model: Callable[[Deployment], Model]
    ):
        def check(dpl, pttrn):
            return matches_regex(
                pattern=pttrn,
                string=getattr(get_model(dpl), arg).value
            )

        self._filters.append(self._new_filter_from_check(check, pattern))

    def _add_filter_for_dict_arg(
        self,
        arg: str,
        pattern: Pattern,
        get_model: Callable[[Deployment], Model],
        get_attr: Callable[[Model], AttributeValue]
    ):
        def check(dpl, pttrn):
            return any(
                matches_regex(pttrn, str(get_attr(model).value))
                for model in getattr(get_model(dpl), arg).value.values()
            )

        self._filters.append(self._new_filter_from_check(check, pattern))

    def _new_filter_from_check(self, check: Check, pattern: Pattern) -> Filter:
        return functools.partial(
            lambda dpl, pttrn, *_: check(dpl, pttrn),
            pttrn=pattern
        )

    def _add_filter_for_nodes_arg(
        self,
        role: str,
        test: Range,
        get_nodes: Callable[[Deployment], Iterable[Node]]
    ):
        def check(dpl):
            # Comparison function used by the test
            run_test = RANGE_OPERATORS[test.operator]

            # List of nodes belonging to the filtered role
            nodes = [
                node for node in get_nodes(dpl)
                if node.role.value == role
            ]

            return run_test(len(nodes), int(test.operand))

        self._filters.append(check)

    def is_valid_deployment(self, deployment):
        """Checks whether a deployment is valid and should be returned as
        part of the query output.

        :param deployment: The deployment to check.
        :type deployment: :class:`Deployment`
        :return: Whether it passes all filters in this instance or not.
        :rtype: bool
        """
        for check in self.filters:
            if not check(deployment):
                return False

        return True
