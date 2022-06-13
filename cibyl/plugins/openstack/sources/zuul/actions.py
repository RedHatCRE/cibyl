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
from dataclasses import dataclass

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.sources.zuul.release import ReleaseFinder
from cibyl.sources.zuul.output import QueryOutputBuilder
from cibyl.sources.zuul.queries.jobs import perform_jobs_query


class DeploymentGenerator:
    class Tools:
        release_finder = ReleaseFinder()

    def __init__(self, tools=Tools()):
        self._tools = tools

    def generate_deployment_for(self, variant, **kwargs):
        """

        :param variant:
        :type variant: :class:`cibyl.sources.zuul.transactions.VariantResponse`
        :return:
        """

        def get_release():
            if 'spec' in kwargs:
                return release_finder.find_release_for(variant)

            if 'release' in kwargs:
                return release_finder.find_release_for(variant)

            return ''

        release_finder = self._tools.release_finder

        return Deployment(
            release=get_release(),
            infra_type='',
            nodes={},
            services={}
        )


def _default_job_query(api, **kwargs):
    return perform_jobs_query(api, **kwargs)


def _default_variant_query(job, **kwargs):
    return job.variants().get()


class DeploymentQuery:
    @dataclass
    class Queries:
        jobs = staticmethod(_default_job_query)
        variants = staticmethod(_default_variant_query)

    @dataclass
    class Tools:
        deployment_generator = DeploymentGenerator()
        output_builder = QueryOutputBuilder()

    def __init__(self, api, queries=Queries(), tools=Tools()):
        self._api = api
        self._queries = queries
        self._tools = tools

    def perform_query(self, **kwargs):
        output = self._tools.output_builder
        dgen = self._tools.deployment_generator

        if 'spec' in kwargs:
            kwargs['jobs'] = kwargs.pop('spec')

        for job in self._queries.jobs(self._api, **kwargs):
            for variant in self._queries.variants(job, **kwargs):
                model = output.with_variant(variant)
                model.deployment.value = dgen.generate_deployment_for(
                    variant, **kwargs
                )

        return output.assemble()
