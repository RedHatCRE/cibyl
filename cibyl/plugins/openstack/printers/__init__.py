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

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.test_collection import TestCollection


class OSPrinter(ABC):
    """Base class for all printers for a OS model tree.
    """

    @abstractmethod
    def print_deployment(self, deployment: Deployment) -> str:
        """
        :param deployment: The deployment.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError

    @abstractmethod
    def print_test_collection(self, collection: TestCollection) -> str:
        """
        :param collection: The collection.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError

    @abstractmethod
    def print_node(self, node: Node) -> str:
        """
        :param node: The node.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError

    @abstractmethod
    def print_container(self, container: Container) -> str:
        """
        :param container: The container.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError

    @abstractmethod
    def print_package(self, package: Package) -> str:
        """
        :param package: The package.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError

    @abstractmethod
    def print_service(self, service: Service) -> str:
        """
        :param service: The service.
        :return: Textual representation of the provided model.
        """
        raise NotImplementedError
