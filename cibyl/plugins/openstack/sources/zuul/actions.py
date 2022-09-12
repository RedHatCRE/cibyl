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
from dataclasses import dataclass, field

from cibyl.plugins.openstack.sources.zuul.deployments.arguments import \
    SpecArgumentHandler
from cibyl.plugins.openstack.sources.zuul.deployments.filtering import \
    DeploymentFiltering
from cibyl.plugins.openstack.sources.zuul.deployments.generator import \
    DeploymentGenerator
from cibyl.sources.zuul.output import QueryOutputBuilder
from cibyl.sources.zuul.queries.jobs import perform_jobs_query

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
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved variants.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.VariantResponse`]
    """
    return job.variants().get()


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
        deployment_generator: DeploymentGenerator = field(
            default_factory=lambda: DeploymentGenerator()
        )
        """Generates the deployment model."""
        spec_arg_handler: SpecArgumentHandler = field(
            default_factory=lambda: SpecArgumentHandler()
        )
        """Indicates which jobs are to be fetched."""
        deployment_filter: DeploymentFiltering = field(
            default_factory=lambda: DeploymentFiltering()
        )
        """Allows to filter out undesired deployments."""
        output_builder: QueryOutputBuilder = field(
            default_factory=lambda: QueryOutputBuilder()
        )
        """Builds the query output."""

    def __init__(self, api, queries=None, tools=None):
        """Constructor.

        :param api: API to interact with Zuul with.
        :type api: :class:`cibyl.sources.zuul.apis.ZuulAPI`
        :param queries: Functions this uses to get the data it works with.
            'None' to allow this to build its own.
        :type queries: :class:`DeploymentQuery.Queries` or None
        :param tools: Utilities this uses to achieve its function.
            'None' to allow this to build its own.
        :type tools: :class:`DeploymentQuery.Tools` or None
        """
        if queries is None:
            queries = DeploymentQuery.Queries()

        if tools is None:
            tools = DeploymentQuery.Tools()

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
