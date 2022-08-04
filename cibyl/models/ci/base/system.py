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
from abc import abstractmethod
from copy import deepcopy
from typing import Dict, List, Type

from cibyl.cli.argument import Argument
from cibyl.exceptions.model import NonSupportedModelType
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.job import Job
from cibyl.models.model import Model
from cibyl.models.product.feature import Feature
from cibyl.sources.source import Source


class System(Model):
    """Base model for a CI system.

    Holds basic information such as the system's name or its type.

    :ivar top_level_model: Defines the model that is the direct child of
        this system. For most system's, this will be :class:`Job`.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'system_type': {
            'attr_type': str,
            'arguments': [
                Argument(name='--system-type', arg_type=str,
                         description="System type")
            ]
        },
        'sources': {
            'attr_type': Source,
            'attribute_value_class': AttributeListValue,
            'arguments': [
                Argument(name='--sources', arg_type=str,
                         nargs="*",
                         description="Source name")
            ]
        },
        'enabled': {
            'attr_type': bool,
            'arguments': []
        },
        'queried': {
            'attr_type': bool,
            'arguments': []
        },
        'features': {
            'attr_type': Feature,
            'attribute_value_class': AttributeDictValue,
            'arguments': []
        },
    }
    """Defines the CLI arguments for all systems.
    """

    def __init__(self, name: str,
                 system_type: str,
                 top_level_model: Type[Model],
                 sources: List = None,
                 enabled: bool = True,
                 **kwargs):
        # Let IDEs know this class's attributes
        self.name = None
        self.system_type = None
        self.sources = None
        self.enabled = None
        self.queried = None

        # Set up the model
        super().__init__(
            {
                'name': name,
                'system_type': system_type,
                'sources': sources,
                'enabled': enabled,
                'queried': False,
                **kwargs
            }
        )

        self.top_level_model = top_level_model

    @abstractmethod
    def add_toplevel_model(self, model):
        """Adds a top-level model to the system. This will be different
        depending on the system type so it is left empty and will be overloaded
        by each type.
        """
        raise NotImplementedError

    def add_source(self, source):
        """Add a source to the CI system.

        :param source: Source to add.
        :type source: :class:`Source`
        """
        self.sources.append(source)

    def enable(self):
        """Enable a system for querying."""
        self.enabled.value = True

    def is_enabled(self):
        """Check whether a system is enabled.

        :returns: Whether the system is enabled
        :rtype: bool
        """
        return self.enabled.value

    def register_query(self):
        """Record that the system was queried."""
        self.queried.value = True

    def is_queried(self):
        """Check whether a system was queried.

        :returns: Whether the system was queried
        :rtype: bool
        """
        return self.queried.value

    def export_attributes_to_source(self):
        """Prepare system-level attributes that should be passed to the
        sources.

        :returns: Dictionary of attributes that should be passed to the sources
        when calling on of their methods
        :rtype: dict
        """
        return {}

    def populate(self, instances):
        """Adds all models found on an attribute to this system.

        :param instances: The attribute to read.
        :type instances: :class:`AttributeValue`
        """
        if instances.attr_type == self.top_level_model:
            for model in instances.values():
                self.add_toplevel_model(model)
        else:
            raise NonSupportedModelType(instances.attr_type)

    def add_feature(self, feature):
        """Add a feature to the system."""
        self.features[feature.name.value] = feature

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.name.value == other.name.value


class JobsSystem(System):
    """Model a system with :class:`Job` as its top-level model.
    """
    API = deepcopy(System.API)
    API.update({
        'jobs': {
            'attr_type': Job,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--jobs', arg_type=str,
                                   nargs='*',
                                   description="System jobs",
                                   func='get_jobs')]}})

    def __init__(self,
                 name: str,
                 system_type: str,
                 sources: List = None,
                 enabled: bool = True,
                 jobs: Dict[str, Job] = None,
                 jobs_scope: str = None):
        # Let IDEs know this class's attributes
        self.jobs = jobs
        # jobs_scope does not need to go through the Model __init__ since it's
        # not in the API. As a result, it's value is stored in a simple string
        # and not in an Argument object
        self.jobs_scope = jobs_scope

        # Set up model
        super().__init__(
            name=name,
            system_type=system_type,
            top_level_model=Job,
            sources=sources,
            enabled=enabled,
            jobs=jobs  # pass jobs to parent init so it's not overriden
        )

    def export_attributes_to_source(self):
        """Prepare system-level attributes that should be passed to the
        sources.

        :returns: Dictionary of attributes that should be passed to the sources
        when calling on of their methods
        :rtype: dict
        """
        return {'jobs_scope': self.jobs_scope}

    def add_toplevel_model(self, model: Job):
        """Adds a top-level model to the system.

        :param model: Job to add.
        :type model: :class:`Job`
        """
        self.add_job(model)

    def add_job(self, job: Job):
        """Adds a job to the CI system. The job will only be added if it's
        consistent with the jobs_scope attribute of the system.

        :param job: Job to add.
        :type job: :class:`Job`
        """
        key = job.name.value

        if key in self.jobs:
            self.jobs[key].merge(job)
        else:
            self.jobs[key] = job
