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
import logging
from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.specs.abc import SCMSpec

LOG = logging.getLogger(__name__)

T = TypeVar('T', bound=SCMSpec)
"""Type for the kind of spec used by backend."""


class ZuulDBackend(Generic[T]):
    """Base class for APIs that allow Cibyl to interact with Zuul.D providers.

    A Zuul.D provider is considered to be any storage that holds Zuul
    definition files in it. These are the files that describe many of the
    elements that take part on a Zuul instance, such as jobs or pipelines.

    An example of a Zuul.D provider may be a Git or SVN repository.
    """

    class Get(ABC):
        """Base class for APIs that focus on read operations.
        """

        @property
        @abstractmethod
        def name(self):
            raise NotImplementedError

        @abstractmethod
        def jobs(self, spec: T) -> Iterable[Job]:
            """Retrieves all jobs defined under the spec.

            :param spec:
                Describes the repository and location within where the
                Zuul.D files are located at.
            :return:
                A transcription of all job objects found under the files
                declared at the spec.
            :raises ZuulDError:
                If the backend failed to retrieve the data.
            """
            raise NotImplementedError

    def __init__(self, get: Get):
        """Constructor.

        :param get: The backend that will support read operations.
        """
        self._get = get

    @property
    def get(self) -> Get:
        """
        :return:
            Interface for performing read operations against Zuul.D
            providers.
        """
        return self._get
