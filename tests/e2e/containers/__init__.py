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
import subprocess
from abc import ABC, abstractmethod

import requests
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


@wait_container_is_ready()
def wait_for(url):
    response = requests.get(url)
    response.raise_for_status()


class DockerComposition(DockerCompose):
    def run_in_container(self, service_name, command):
        run_cmd = self.docker_compose_command() \
                  + ['run', '--rm', service_name] \
                  + command

        result = subprocess.run(
            run_cmd,
            cwd=self.filepath,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return \
            result.stdout.decode("utf-8"), \
            result.stderr.decode("utf-8"), \
            result.returncode


class ComposedContainer(ABC):
    def __init__(self, filedir, filename='docker-compose.yml'):
        self._container = DockerComposition(
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
        raise NotImplementedError

    def start(self):
        self._container.start()
        self._wait_until_ready()
        self._on_ready()

    def run(self, service, command):
        return self._container.run_in_container(service, command)

    def stop(self):
        self._container.stop()

    def _on_ready(self):
        # Do nothing by default
        return
