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
from cibyl.models.ci.zuul.pipeline import Pipeline
from cibyl.models.model import Model


class Project(Model):
    """Representation of a Zuul project.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'url': {
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

    def __init__(self, name, url, pipelines=None):
        # Let IDEs know this model's attributes
        self.name = None
        self.url = None
        self.pipelines = None

        # Set up the model
        super().__init__({'name': name, 'url': url, 'pipelines': pipelines})

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False

        if self.pipelines != other.pipelines:
            return False

        return self.name == other.name and self.url == other.url

    def merge(self, other):
        """Adds the contents of another project into this one.

        :param other: The other project.
        :type other: :class:`Project`
        """
        for pipeline in other.pipelines.values():
            self.add_pipeline(pipeline)

    def add_pipeline(self, pipeline):
        """Appends, or merges, a new child pipeline into this project.

        If the pipeline already exists in this project, then it is not
        overwritten. Instead, the two pipelines are merged together into a
        complete pipeline model.

        :param pipeline: The pipeline to be added.
        :type pipeline: :class:`Pipeline`
        """
        key = pipeline.name.value

        if key in self.pipelines:
            # Extract unknown contents of pipeline
            self.pipelines[key].merge(pipeline)
        else:
            # Register brand-new pipeline
            self.pipelines[key] = pipeline
