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
from abc import ABC, abstractmethod


class PipelinesProvider(ABC):
    """Represents an entity capable of retrieving information on pipelines.
    """

    @property
    @abstractmethod
    def name(self):
        """
        :return: Name of the provider.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def pipelines(self):
        """
        :return: The pipelines from this entity.
        :rtype: list[:class:`cibyl.sources.zuul.apis.ZuulPipelineAPI`]
        """
        raise NotImplementedError


class JobsProvider(ABC):
    """Represents an entity capable of retrieving information on jobs.
    """

    @property
    @abstractmethod
    def name(self):
        """
        :return: Name of the provider.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def jobs(self):
        """
        :return: The jobs from this entity.
        :rtype: list[:class:`cibyl.sources.zuul.apis.ZuulJobAPI`]
        """
        raise NotImplementedError
