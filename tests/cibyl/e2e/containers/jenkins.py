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
from pathlib import Path

import requests
from overrides import overrides

from tests.cibyl.e2e.containers import ComposedContainer, wait_for


class JenkinsContainer(ComposedContainer):
    def __init__(self, compose_file='docker-compose.yml'):
        """Constructor.

        :param filename: Name of the 'docker-compose' file to read.
        :type filename: str
        """
        super().__init__('tests/cibyl/e2e/data/images/jenkins',
                         filename=compose_file)

    @property
    def url(self):
        # Defined on dockerfile
        return 'http://localhost:8080'

    @overrides
    def _wait_until_ready(self):
        wait_for(f'{self.url}/api/json')

    def add_job(
        self, name,
        config='tests/cibyl/e2e/data/images/jenkins/jobs/basic-job-config.xml',
        credentials=None
    ):
        """Adds a new job on the Jenkins host.

        :param name: Name of the job.
        :type name: str
        :param config: Path to the job's XML description file.
        :type config: str
        :param credentials: User and password used to perform the action.
        :type credentials: Any or None
        :raise FileNotFoundError: If the definition file does not exists.
        :raise HTTPError: If the request failed.
        """
        requests.post(
            url=f'{self.url}/createItem?name={name}',
            auth=credentials,
            headers={'Content-Type': 'application/xml'},
            data=Path(config).read_text('utf-8')
        ).raise_for_status()
