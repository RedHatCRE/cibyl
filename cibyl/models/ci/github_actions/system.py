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
from cibyl.models.ci.github_actions.workflow import Workflow


class WorkflowsSystem(System):
    """Model a system with :class:`Workflow` as its top-level model.
    """
    API = deepcopy(System.API)
    API.update(
        {
            'workflows': {
                'attr_type': Workflow,
                'attribute_value_class': AttributeDictValue,
                'arguments': [
                    Argument(name='--workflows', arg_type=str,
                             nargs='*',
                             description='Repository Workflows',
                             func='get_workflows')
                ]
            }
        }
    )

    def __init__(self,
                 name,
                 system_type='github_action',
                 sources=None,
                 enabled=True,
                 workflows=None):
        self.workflows = workflows

        # Set up model
        super().__init__(
            name=name,
            system_type=system_type,
            top_level_model=Workflow,
            sources=sources,
            enabled=enabled,
            workflows=workflows
        )

    def add_toplevel_model(self, model):
        key = model.name.value

        if key in self.workflows:
            # Extract unknown contents of workflow
            self.workflows[key].merge(model)
        else:
            # Add a brand-new workflow
            self.workflows[key] = model
