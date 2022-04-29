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
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.pipeline import Pipeline
from cibyl.models.model import Model


class Project(Model):
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'pipelines': {
            'attr_type': Pipeline,
            'attribute_value_class': AttributeDictValue,
            'arguments': [
                Argument(
                    name='--pipelines',
                    arg_type=str, nargs='*',
                    description='Pipelines belonging to project',
                    func='get_pipelines'
                )
            ]
        }
    }

    def __init__(self, name, pipelines=None):
        # Let IDEs know this model's attributes
        self.name = None
        self.pipelines = None

        # Set up the model
        super().__init__({'name': name, 'pipelines': pipelines})

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False

        return self.name == other.name

    def merge(self, other):
        """

        :param other:
        :type other: :class:`Project`
        :return:
        """
        for pipeline in other.pipelines.values():
            self.add_pipeline(pipeline)

    def add_pipeline(self, pipeline):
        """

        :param pipeline:
        :type pipeline: :class:`Pipeline`
        :return:
        """
        key = pipeline.name.value

        if key in self.pipelines:
            # Extract unknown contents of pipeline
            self.pipelines[key].merge(pipeline)
        else:
            # Register brand-new pipeline
            self.pipelines[key] = pipeline
