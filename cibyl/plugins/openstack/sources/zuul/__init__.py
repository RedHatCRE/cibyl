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
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.plugins.openstack import Deployment
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source import speed_index
from cibyl.sources.zuul.output import QueryOutputBuilder
from cibyl.sources.zuul.queries.jobs import perform_jobs_query


class Zuul(SourceExtension):
    """
    @DynamicAttrs: Will use attributes of source it extends.
    """

    @speed_index({'base': 2})
    def get_deployment(self, **kwargs):
        output_builder = QueryOutputBuilder()

        if 'spec' in kwargs:
            kwargs['jobs'] = kwargs.pop('spec')

        for job in perform_jobs_query(self._api, **kwargs):
            model = output_builder.with_job(job)
            model.deployment.value = self._generate_deployment_for(job)

        return AttributeDictValue(
            name='tenants',
            attr_type=Tenant,
            value=output_builder.assemble()
        )

    def _generate_deployment_for(self, job):
        return Deployment(
            release='',
            infra_type='',
            nodes={},
            services={}
        )
