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
import json
from abc import ABC
from typing import Callable, Union

from overrides import overrides

from cibyl.cli.query import QueryType
from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.printers import OSPrinter
from cibyl.plugins.openstack.service import Service


class OSSerializedPrinter(OSPrinter, ABC):
    def __init__(
        self,
        load_function: Callable[[str], dict],
        dump_function: Callable[[dict], str],
        query: QueryType = QueryType.NONE,
        verbosity: int = 0
    ):
        super().__init__(query, verbosity)

        self._load = load_function
        self._dump = dump_function

    @overrides
    def print_deployment(self, deployment: Deployment) -> str:
        result = {
            'release': deployment.release.value,
            'infra_type': deployment.infra_type.value,
            'topology': deployment.topology.value
        }

        return self._dump(result)

    @overrides
    def print_node(self, node: Node) -> str:
        pass

    @overrides
    def print_container(self, container: Container) -> str:
        pass

    @overrides
    def print_package(self, package: Package) -> str:
        pass

    @overrides
    def print_service(self, service: Service) -> str:
        pass


class OSJSONPrinter(OSSerializedPrinter):
    def __init__(
        self,
        query: QueryType = QueryType.NONE,
        verbosity: int = 0,
        indentation: int = 4
    ):
        """Constructor. See parent for more information.

        :param indentation: Number of spaces indenting each level of the
            JSON output.
        """
        super().__init__(
            load_function=self._from_json,
            dump_function=self._to_json,
            query=query,
            verbosity=verbosity
        )

        self._indentation = indentation

    @property
    def indentation(self) -> int:
        """
        :return: Number of spaces preceding every level of the JSON output.
        """
        return self._indentation

    def _from_json(self, obj: Union[str, bytes, bytearray]) -> dict:
        return json.loads(obj)

    def _to_json(self, obj: object) -> str:
        return json.dumps(obj, indent=self._indentation)
