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

import requests
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready

from cibyl.exceptions import CibylNotImplementedException


@wait_container_is_ready()
def wait_for(url):
    response = requests.get(url)
    response.raise_for_status()


class ComposedContainer(ABC):
    def __init__(self, filedir, filename='docker-compose.yml'):
        self._container = DockerCompose(
            filepath=filedir,
            compose_file_name=filename,
            pull=True
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @abstractmethod
    def _wait_until_ready(self):
        raise CibylNotImplementedException

    def start(self):
        self._container.start()
        self._wait_until_ready()
        self._on_ready()

    def stop(self):
        self._container.stop()

    def _on_ready(self):
        # Do nothing by default
        return
