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

from cibyl.output import Printer


class CIPrinter(Printer, ABC):
    """Base class for all printers for a CI model tree.
    """

    @abstractmethod
    def print_environment(self, env):
        """
        :param env: The environment.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_system(self, system):
        """
        :param system: The system.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_tenant(self, tenant):
        """
        :param tenant: The tenant.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_project(self, project):
        """
        :param project: The project.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_pipeline(self, pipeline):
        """
        :param pipeline: The pipeline.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_job(self, job):
        """
        :param job: The job.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_build(self, build):
        """
        :param build: The build.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def print_test(self, test):
        """
        :param test: The test.
        :return: Textual representation of the provided model.
        :rtype: str
        """
        raise NotImplementedError
