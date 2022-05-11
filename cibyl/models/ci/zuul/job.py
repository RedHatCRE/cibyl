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
from overrides import overrides

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeListValue, AttributeDictValue
from cibyl.models.ci.job import Job as BaseJob
from cibyl.models.model import Model


class Job(BaseJob):
    """
    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Variant(Model):
        """
        @DynamicAttrs: Contains attributes added on runtime.
        """
        API = {
            'parent': {
                'attr_type': str,
                'arguments': []
            },
            'description': {
                'attr_type': str,
                'arguments': []
            },
            'branches': {
                'attr_type': str,
                'attribute_value_class': AttributeListValue,
                'arguments': []
            },
            'variables': {
                'attr_type': str,
                'attribute_value_class': AttributeDictValue,
                'arguments': []
            }
        }

        def __init__(self,
                     parent,
                     description=None,
                     branches=None,
                     variables=None):
            super().__init__(
                {
                    'parent': parent,
                    'description': description,
                    'branches': branches,
                    'variables': variables
                }
            )

        @staticmethod
        def from_data(data):
            return Job.Variant(
                parent=data.get('parent', 'Unknown'),
                description=data.get('description'),
                branches=data.get('branches'),
                variables=data.get('variables')
            )

        def __eq__(self, other):
            if not isinstance(other, Job.Variant):
                return False

            if self is other:
                return True

            return \
                self.parent == other.parent and \
                self.description == other.description and \
                self.branches == other.branches and \
                self.variables == other.variables

    API = {
        **BaseJob.API,
        'variants': {
            'attr_type': Variant,
            'attribute_value_class': AttributeListValue,
            'arguments': [
                Argument(
                    name='--variants', arg_type=None, nargs=0,
                    func='get_jobs', description='Fetch job variants'
                )
            ]
        }
    }

    def __init__(self, name, url, variants=None, builds=None):
        super().__init__(name, url, builds, variants=variants)

    @overrides
    def merge(self, other):
        super().merge(other)

        for variant in other.variants:
            self.add_variant(variant)

    def add_variant(self, variant):
        self.variants.append(variant)
