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
from cibyl.cli.query import QuerySelector, QueryType
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.zuul.job import Job as ZuulJob
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.utils.dicts import subset


def add_deployment(self, deployment: Deployment):
    """Add a deployment to the job.

    :param deployment: Deployment to add to the job
    :type deployment: :class:`.Deployment`
    """
    self.deployment.value = deployment


def get_query_openstack(**kwargs):
    """Deduce the query type from openstack cli arguments."""
    result = QueryType.NONE
    possible_deployment_args = []
    for attr_options in Deployment.API.values():
        for cli_arg in attr_options.get('arguments', []):
            # remove leading '-' in cli argument
            cli_arg_name = cli_arg.name.strip("-")
            # replace separator '-' by '_', since that is the way the parser
            # stores the arguments
            possible_deployment_args.append(cli_arg_name.replace("-", "_"))

    deployment_args = subset(kwargs, possible_deployment_args)
    if deployment_args:
        result = QueryType.JOBS

    return result


class Plugin:
    """Extend a CI model with Openstack specific models and methods."""
    plugin_attributes_to_add = {
        'deployment': {'add_method': 'add_deployment'}
        }

    def extend_models(self):
        def get_deployment_api():
            return {
                'attr_type': Deployment,
                'arguments': [
                    Argument(
                        name="--deployment",
                        arg_type=str,
                        nargs="*",
                        description="Openstack deployment")
                ]
            }

        def extend_job_model():
            plugin_attributes = self.plugin_attributes_to_add

            Job.API['deployment'] = get_deployment_api()
            Job.plugin_attributes.update(plugin_attributes)

            setattr(Job, 'add_deployment', add_deployment)

        def extend_variant_model():
            plugin_attributes = self.plugin_attributes_to_add

            ZuulJob.Variant.API['deployment'] = get_deployment_api()
            ZuulJob.Variant.plugin_attributes.update(plugin_attributes)

            setattr(ZuulJob.Variant, 'add_deployment', add_deployment)

        extend_job_model()
        extend_variant_model()

    def extend_query_types(self):
        QuerySelector.query_selector_functions.append(get_query_openstack)
