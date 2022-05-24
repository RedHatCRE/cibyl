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
from requests.exceptions import ConnectionError, HTTPError
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


@wait_container_is_ready(ConnectionError, HTTPError)
def wait_for(url):
    """Utility that polls a URL until it starts responding. Useful to block
    runtime until a host is up.

    For information on the polling, see :func:`wait_container_is_ready`.

    :param url: The URL to poll.
    :type url: str
    """
    response = requests.get(url)
    response.raise_for_status()


class DockerComposition(DockerCompose):
    """Handler for a 'docker-compose' file.
    """

    def run_in_container(self, service_name, command):
        """Instantiates a container for one of the services and runs a
        command in it. The container's instance gets deleted once the
        command finishes.

        :param service_name: Name of the docker compose service to run the
            command in.
        :type service_name: str
        :param command: The command to execute.
        :type command: list[str]
        :return: stout, stderr, return code
        :rtype: tuple[str, str, int]
        """
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
    """Base class for all Docker environments generated from a
    'docker-compose'.
    """

    def __init__(self, filedir, filename='docker-compose.yml'):
        """Constructor.

        :param filedir: Directory where the 'docker-compose' yaml is found at.
        :type filedir: str
        :param filename: Name of the 'docker-compose' file to read.
        :type filename: str
        """
        self._container = DockerComposition(
            filepath=filedir,
            compose_file_name=filename,
            pull=False, build=True
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @abstractmethod
    def _wait_until_ready(self):
        """Callback called after the container is started meant to give time
        for it to be fully operational.
        """
        raise NotImplementedError

    def start(self):
        """Start the container.
        """
        self._container.start()
        self._wait_until_ready()
        self._on_ready()

    def run(self, service, command):
        """Runs a command on one of the services of the compose.

        :param service: Name of the docker compose service to invoke.
        :type service: str
        :param command: The command to run in the container.
        :type command: list[str]
        :return: stdout, stderr, return_code
        :rtype: type[str, str, int]
        """
        return self._container.run_in_container(service, command)

    def stop(self):
        """Stops the container.
        """
        self._container.stop()

    def _on_ready(self):
        """Callback called after the container is ready meant to perform
        post-start actions on the container.
        """
        # Do nothing by default
        return
