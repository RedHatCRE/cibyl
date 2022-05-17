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
from cibyl.cli.argument import Argument
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.zuul.job import Job as ZuulJob
from cibyl.plugins.openstack.deployment import Deployment


def add_deployment(self, deployment: Deployment):
    """Add a deployment to the job.

    :param deployment: Deployment to add to the job
    :type deployment: :class:`.Deployment`
    """
    self.deployment.value = deployment


class Plugin:
    """Extend a CI model with Openstack specific models and methods."""
    plugin_attributes_to_add = {
        'deployment': {'add_method': 'add_deployment'}
        }

    def extend_models(self):
        for job_class in [Job, ZuulJob]:
            job_class.API['deployment'] = {
                'attr_type': Deployment,
                'arguments': [Argument(
                    name="--deployment",
                    arg_type=str,
                    nargs="*",
                    description="Openstack deployment")]}
            job_class.plugin_attributes.update(
                    self.plugin_attributes_to_add)
            setattr(job_class, 'add_deployment',
                    add_deployment)
