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
    """Base fixture for e2e tests. Redirects stdout to a buffer to help
    assert the app's output.
    """

    def setUp(self):
        self._buffer = StringIO()

        sys.stdout = self._buffer

    @property
    def output(self):
        """
        :return: What the app wrote to stdout.
        :rtype: str
        """
        return self._buffer.getvalue()


class JenkinsTest(EndToEndTest):
    """Spawns a container with a simple Jenkins installation for tests to
    work over.

    :ivar jenkins: The Jenkins' container driver.
    """

    jenkins = None

    @classmethod
    def setUpClass(cls):
        # Define the image
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
    """Spawns a container with a simple Zuul installation for tests to
    work over. The installation follows the guide described here:
    `Zuul Quick-Start
    <https://zuul-ci.org/docs/zuul/latest/tutorials/quick-start.html>`_.

    :ivar dir: A directory where zuul's repository is cloned into.
    :ivar zuul: The Zuul' container driver.
    """

    dir = None
    zuul = None

    @classmethod
    def setUpClass(cls):
        # Download Zuul example's docker description
        cls.dir = TemporaryDirectory()

        Repo.clone_from('https://opendev.org/zuul/zuul', cls.dir.name)

        # Define the image
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


class ElasticSearchTest(EndToEndTest):
    elasticsearch = None

    @classmethod
    def setUpClass(cls):
        # Define the image
        cls.elasticsearch = DockerCompose(
            filepath='tests/e2e/images/elasticsearch',
            pull=True
        )

        # Launch the container
        cls.elasticsearch.start()

        # Wait for ElasticSearch to be ready
        wait_for('http://localhost:9200')

        # Prepare database
        jenkins_mapping = 'tests/e2e/images/elasticsearch/jenkins.mapping.json'

        with open(jenkins_mapping, 'r') as mapping:
            # Create the index
            requests.put(
                'http://localhost:9200/jenkins'
            )

            # It is a big mapping, increase the number of possible fields
            requests.put(
                'http://localhost:9200/jenkins/_settings',
                json={
                    'index.mapping.total_fields.limit': 2000
                }
            )

            # Load the mapping
            requests.put(
                'http://localhost:9200/jenkins/_mapping',
                json=json.load(mapping)
            )

    @classmethod
    def tearDownClass(cls):
        cls.elasticsearch.stop()
