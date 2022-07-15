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
from typing import Callable

from cibyl.cli.argument import Argument
from cibyl.models.model import Model
from cibyl.plugins.openstack import Deployment
from cibyl.utils.filtering import matches_regex

Filter = Callable[[Deployment], bool]
"""Type of the filters stored in this class."""


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
    def filters(self):
        return self._filters

    def add_filters_from(self, **kwargs):
        """Generates and adds to this filters coming from the command line
        arguments. The arguments are interpreted, the filters generated from
        them and then appended to the list of filters already present here.

        :param kwargs: The command line arguments.
        """
        deployment_args = (
            'release',
            'infra_type',
            'topology'
        )

        for arg in deployment_args:
            self._handle_arg_filter(
                arg,
                lambda dpl: dpl,
                **kwargs
            )

        network_args = (
            'network_backend',
            'ip_version',
        )

        for arg in network_args:
            self._handle_arg_filter(
                arg,
                lambda dpl: dpl.network.value,
                **kwargs
            )

        storage_args = (
            'cinder_backend',
        )

        for arg in storage_args:
            self._handle_arg_filter(
                arg,
                lambda dpl: dpl.storage.value,
                **kwargs
            )

    def _handle_arg_filter(
        self,
        arg: str,
        attr: Callable[[Deployment], Model],
        **kwargs: Argument
    ) -> None:
        if arg not in kwargs:
            return

        patterns = kwargs[arg].value

        if not patterns:
            return

        for pattern in patterns:
            self.filters.append(
                functools.partial(
                    lambda dpl, pat: matches_regex(
                        pat, getattr(attr(dpl), arg).value
                    ),
                    pat=pattern
                )
            )

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
