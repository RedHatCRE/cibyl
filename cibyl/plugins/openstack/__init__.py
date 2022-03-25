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
from cibyl.plugins.openstack.deployment import Deployment

API_CLASS = {
    "deployment": Deployment
}


class ExtendPlugin:
    def _extend_model(self, model_name):
        for attr_type, attr_value in model_name.items():
            if 'attr_type' in attr_value.keys() and \
               attr_value['attr_type'].__name__ == "Job":
                for key, values in API_CLASS.items():
                    attr_value['attr_type'].API[key] = {
                        'attr_type': values,
                        'arguments': [Argument(
                            name="--deployment",
                            arg_type=str,
                            nargs="*",
                            description="Openstack deployment")]}

            if hasattr(attr_value['attr_type'], 'API'):
                self._extend_model(attr_value['attr_type'].API)
