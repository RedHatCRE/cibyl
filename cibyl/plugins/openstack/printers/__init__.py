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

from cibyl.publisher import Printer


class OpenStackPrinter(ABC, Printer):
    @abstractmethod
    def print_container(self):
        raise NotImplementedError

    @abstractmethod
    def print_deployment(self):
        raise NotImplementedError

    @abstractmethod
    def print_node(self):
        raise NotImplementedError

    @abstractmethod
    def print_package(self):
        raise NotImplementedError

    @abstractmethod
    def print_service(self):
        raise NotImplementedError
