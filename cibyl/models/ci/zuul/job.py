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
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.job import Job as BaseJob
from cibyl.models.model import Model
from cibyl.utils.dicts import subset


class Job(BaseJob):
    """Representation of a job on a zuul environment.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Variant(Model):
        """Representation of a job variant on a zuul environment.

        @DynamicAttrs: Contains attributes added on runtime.
        """
        API = {
            'parent': {
                'attr_type': str,
                'arguments': []
            },
            'name': {
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
        """Defines the elements that compose this model.
        """

        def __init__(self,
                     parent, name,
                     description=None,
                     branches=None,
                     variables=None):
            """Constructor.

            :param parent: Name of the parent job of this variant.
            :type: parent: str
            :param name: Name of the variant.
            :type name: str
            :param description: Description of the variant.
            :type description: str
            :param branches: Branches the variant targets.
            :type branches: list[str]
            :param variables: Preset of variables that define the variant.
            :type variables: dict[str, Any]
            """
            super().__init__(
                {
                    'parent': parent,
                    'name': name,
                    'description': description,
                    'branches': branches,
                    'variables': variables
                }
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
        **subset(BaseJob.API, ['name', 'url', 'builds']),
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
    """Defines the data that composes this model and where it is retrieved
    from.
    """

    def __init__(self, name, url, variants=None, builds=None):
        """Constructor. See parent constructor for more info.

        :param variants: Variant that derive this job.
        :type variants: list[:class:`Job.Variant`]
        """
        super().__init__(name, url, builds, variants=variants)

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False

        if self is other:
            return True

        if self.builds != other.builds:
            return False

        if self.variants != other.variants:
            return False

        return \
            self.name == other.name and \
            self.url == other.url

    @overrides
    def merge(self, other):
        # Merging with oneself will never end, avoid at all costs.
        if self is other:
            return

        # Do the standard merge
        super().merge(other)

        # Add additional steps for this type
        for variant in other.variants:
            self.add_variant(variant)

    def add_variant(self, variant):
        """Adds a new variant to this job. No check is performed to see if
        this job is the parent of the added variant.

        :param variant: The variant.
        :type variant: :class:`Job.Variant`
        """
        self.variants.append(variant)
