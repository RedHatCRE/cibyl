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
from cibyl.models.openstack.deployment import Deployment


class OpenstackPlugin:

    def extend(self, model_api):
        for attr_name, attr_value in model_api.items():
            if 'attr_type' in attr_value and \
               attr_value['attr_type'].__name__ == 'Job':
                attr_value['attr_type'].API['deployment'] = {
                    'attr_type': Deployment,
                    'arguments': []
                }
            if hasattr(attr_value['attr_type'], 'API'):
                self.extend(attr_value['attr_type'].API)
