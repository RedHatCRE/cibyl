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
from dataclasses import dataclass
from enum import Enum
from typing import Any

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.sources.zuul.deployments.filtering import \
    DeploymentFiltering
from cibyl.plugins.openstack.sources.zuul.deployments.outlines import \
    OutlineCreator
from cibyl.plugins.openstack.sources.zuul.variants import ReleaseSearch
from cibyl.sources.zuul.output import QueryOutputBuilder
from cibyl.sources.zuul.queries.jobs import perform_jobs_query
from cibyl.sources.zuul.transactions import VariantResponse
from tripleo.insights import DeploymentLookUp

LOG = logging.getLogger(__name__)


def _default_job_query(api, **kwargs):
    """Retrieves the jobs by querying the Zuul host.

    :param api: API to interact with Zuul with.
    :type api: :class:`cibyl.sources.zuul.apis.ZuulAPI`
    :param kwargs: See :func:`cibyl.sources.zuul.actions.handle_query`.
    :return: List of retrieved jobs.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.JobResponse`]
    """
    return perform_jobs_query(api, **kwargs)


def _default_variant_query(job, **kwargs):
    """Retrieves variants of a job by querying the Zuul host.

    :param job: The job to get the variants for.
    :type job: :class:`cibyl.sources.zuul.transactions.JobResponse`
    :param kwargs: See :func:`handle_query`.
    :return: List of retrieved variants.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.VariantResponse`]
    """
    return job.variants().get()


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


class DeploymentGenerator:
    """Factory for generation of :class:`Deployment`.
    """

    class Tools:
        """Tools the factory will use to do its task.
        """
        outline_creator = OutlineCreator()
        """Tests care of creating the TripleO outline for a Zuul job."""
        deployment_lookup = DeploymentLookUp()
        """Gets additional information on the deployment from TripleO."""
        release_search = ReleaseSearch()
        """Takes care of finding the release of the deployment."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: The tools this will use.
        """
        self._tools = tools

    @property
    def tools(self) -> Tools:
        """
        :return: The tools this will use.
        """
        return self._tools

    def generate_deployment_for(
        self,
        variant: VariantResponse,
        **kwargs: Any
    ) -> Deployment:
        """Creates a new deployment based on the data from a job's variant.

        :param variant: The variant to fetch data from.
        :return: The deployment.
        """
        summary = self.tools.deployment_lookup.run(
            self.tools.outline_creator.new_outline_for(variant)
        )

        return Deployment(
            release=self._get_release(variant, **kwargs),
            infra_type=summary.infra_type,
            topology=summary.topology,
            network=Network(
                ip_version=summary.ip_version
            )
        )

    def _get_release(self, variant: VariantResponse, **kwargs: Any) -> str:
        release_search = self.tools.release_search

        if any(term in kwargs for term in ('spec', 'release')):
            release = release_search.search(variant)

            if not release:
                return 'N/A'

            _, value = release

            return value

        # Nothing means to not output this field.
        return ''


class DeploymentQuery:
    """Takes care of performing the 'get_deployment' query.
    """

    @dataclass
    class Queries:
        """A collection of functions that this uses to perform its task.
        """
        jobs = staticmethod(_default_job_query)
        """Provider of the jobs to get the deployment for."""
        variants = staticmethod(_default_variant_query)
        """Provider of variants on a job."""

    @dataclass
    class Tools:
        """A collection of utilities that this uses to perform its task.
        """
        deployment_generator = DeploymentGenerator()
        """Generates the deployment model."""
        spec_arg_handler = SpecArgumentHandler()
        """Indicates which jobs are to be fetched."""
        deployment_filter = DeploymentFiltering()
        """Allows to filter out undesired deployments."""
        output_builder = QueryOutputBuilder()
        """Builds the query output."""

    def __init__(self, api, queries=Queries(), tools=Tools()):
        """Constructor.

        :param api: API to interact with Zuul with.
        :type api: :class:`cibyl.sources.zuul.apis.ZuulAPI`
        :param queries: Functions this uses to get the data it works with.
        :type queries: :class:`DeploymentQuery.Queries`
        :param tools: Utilities this uses to achieve its function.
        :type tools: :class:`DeploymentQuery.Tools`
        """
        self._api = api
        self._queries = queries
        self._tools = tools

    def perform_query(self, **kwargs):
        """Performs the 'get_deployment' query.

        :param kwargs: Arguments coming from the command line.
        :return: Output of the query.
        :rtype: :class:`cibyl.sources.zuul.output.QueryOutput`
        """

        def get_jobs_query_args():
            result = kwargs.copy()
            option = argh.get_target_jobs(**kwargs)

            if option == SpecArgumentHandler.Option.SPEC:
                # '--spec' has priority over '--jobs'
                result['jobs'] = result.pop('spec')

            return result

        output = self._tools.output_builder
        argh = self._tools.spec_arg_handler
        filters = self._tools.deployment_filter
        dgen = self._tools.deployment_generator

        # Prepare filters beforehand
        filters.add_filters_from(**kwargs)

        for job in self._queries.jobs(self._api, **get_jobs_query_args()):
            for variant in self._queries.variants(job, **kwargs):
                deployment = dgen.generate_deployment_for(variant, **kwargs)

                if filters.is_valid_deployment(deployment):
                    model = output.with_variant(variant)
                    model.deployment.value = deployment

        return output.assemble()
