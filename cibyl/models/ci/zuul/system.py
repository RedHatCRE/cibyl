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
from copy import deepcopy

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.system import System
from cibyl.models.ci.zuul.tenant import Tenant


class ZuulSystem(System):
    """Model a system with :class:`Tenant` as its top-level model.
    """
    API = deepcopy(System.API)
    API.update(
        {
            'tenants': {
                'attr_type': Tenant,
                'attribute_value_class': AttributeDictValue,
                'arguments': [
                    Argument(name='--tenants', arg_type=str,
                             nargs='*',
                             description='System tenants',
                             func='get_tenants')
                ]
            }
        }
    )

    def __init__(self,
                 name,
                 system_type='zuul',
                 sources=None,
                 enabled=True,
                 tenants=None):
        # Let IDEs know this class's attributes
        self.tenants = tenants

        # Set up model
        super().__init__(
            name=name,
            system_type=system_type,
            top_level_model=Tenant,
            sources=sources,
            enabled=enabled,
            # pass tenants to parent init so it's not overriden
            tenants=tenants
        )

    def add_toplevel_model(self, model):
        key = model.name.value

        if key in self.tenants:
            # Extract unknown contents of tenant
            self.tenants[key].merge(model)
        else:
            # Add a brand-new tenant
            self.tenants[key] = model
