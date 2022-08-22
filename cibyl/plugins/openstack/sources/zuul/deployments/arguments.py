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
from enum import Enum
from typing import Any

LOG = logging.getLogger(__name__)


class ArgumentReview:
    """Interprets arguments coming from the CLI and provides their meaning.
    """

    def is_release_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the release to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'release'))

    def is_infra_type_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the infra type to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'infra_type'))

    def is_nodes_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the nodes to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'nodes', 'controllers'))

    def is_topology_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the topology to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'topology'))

    def is_cinder_backend_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the cinder backend to be part
            of the deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'cinder_backend'))

    def is_network_backend_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the network backend to be part
            of the deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'network_backend'))

    def is_ip_version_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested the ip version to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'ip_version'))

    def is_tls_everywhere_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested tls everywhere to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec',))

    def is_ml2_driver_requested(self, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments coming from the CLI.
        :return: True if the user requested ml2 driver to be part of the
            deployment, False if not.
        """
        return any(arg in kwargs for arg in ('spec', 'ml2_driver'))


class SpecArgumentHandler:
    """Figures out which argument holds the jobs to be fetched from the host.
    """

    class Option(Enum):
        NONE = 0
        """Could not determine which argument has the filters."""
        EMPTY = 1
        """Arguments were present, but no filter was defined."""
        JOBS = 2
        """Pick the filters on the 'jobs' arguments."""
        SPEC = 3
        """Pick the filters on the 'spec' arguments."""

    def get_target_jobs(self, **kwargs):
        """Determines the source for the target jobs.

        The rules are:
            - If neither argument is present -> None
            - If just one of the two is present -> Pick that
            - If both are present, but neither have a value -> No filter
            - If both are present, but only one has a value -> Pick that
            - If both are present and have a value -> Prefer '--spec'

        :param kwargs: Tha arguments to study.
        :key jobs: First candidate for provider of target jobs.
            Type: Argument. Default: None.
        :key spec: Second candidate for provider of target jobs.
            Type: Argument. Default: None.
        :return: Option to be taken relative to the provided arguments.
        :rtype: :class:`SpecArgumentHandler.Option`
        """
        if 'jobs' not in kwargs:
            if 'spec' not in kwargs:
                # Neither of the two arguments were passed
                return SpecArgumentHandler.Option.NONE

            # Only 'spec' was passed
            return SpecArgumentHandler.Option.SPEC

        if 'spec' not in kwargs:
            # Only 'jobs' was passed
            return SpecArgumentHandler.Option.JOBS

        if not kwargs['jobs']:
            if not kwargs['spec']:
                # Neither of the two arguments have a value
                return SpecArgumentHandler.Option.EMPTY

            # Only 'spec' has a value
            return SpecArgumentHandler.Option.SPEC

        if not kwargs['spec']:
            # Only 'jobs' has a value
            return SpecArgumentHandler.Option.JOBS

        LOG.warning("Ignoring argument '--jobs' in favor of '--spec'.")

        # If both have a value, prefer 'spec'
        return SpecArgumentHandler.Option.SPEC
