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
import os.path
import sys
from io import StringIO
from tempfile import TemporaryDirectory
from unittest import TestCase

import requests
from git import Repo
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


@wait_container_is_ready()
def wait_for(url):
    response = requests.get(url)
    response.raise_for_status()


class EndToEndTest(TestCase):
    def setUp(self):
        self.buffer = StringIO()

        sys.stdout = self.buffer

    @property
    def output(self):
        return self.buffer.getvalue()


class JenkinsTest(EndToEndTest):
    jenkins = None

    @classmethod
    def setUpClass(cls):
        cls.jenkins = DockerCompose(
            filepath='tests/e2e/images/jenkins',
            pull=True
        )

        # Launch the container
        cls.jenkins.start()

        # Wait for Jenkins to be ready
        wait_for('http://localhost:8080/api/json')

    @classmethod
    def tearDownClass(cls):
        cls.jenkins.stop()


class ZuulTest(EndToEndTest):
    dir = None
    zuul = None

    @classmethod
    def setUpClass(cls):
        cls.dir = TemporaryDirectory()

        Repo.clone_from('https://opendev.org/zuul/zuul', cls.dir.name)

        cls.zuul = DockerCompose(
            filepath=os.path.join(cls.dir.name, 'doc/source/examples'),
            compose_file_name=['docker-compose.yaml'],
            pull=True
        )

        # Launch the container
        cls.zuul.start()

        # Wait for Zuul to be ready
        wait_for('http://localhost:9000/api')

    @classmethod
    def tearDownClass(cls):
        cls.zuul.stop()
        cls.dir.cleanup()
