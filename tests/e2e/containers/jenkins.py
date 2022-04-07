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
import requests
from overrides import overrides

from tests.e2e.containers import ComposedContainer, wait_for


class JenkinsContainer(ComposedContainer):
    def __init__(self):
        super().__init__('tests/e2e/data/images/jenkins')

    @property
    def url(self):
        # Defined on dockerfile
        return 'http://localhost:8080'

    @overrides
    def _wait_until_ready(self):
        wait_for(f'{self.url}/api/json')

    def add_job(
        self, name,
        job_def='tests/e2e/data/images/jenkins/jobs/basic-job-config.xml',
        credentials=('admin', 'passwd')
    ):
        """Adds a new job on the Jenkins host.

        :param name: Name of the job.
        :type name: str
        :param job_def: Path to the job's XML description file.
        :type job_def: str
        :param credentials: User and password used to perform the action.
        :type credentials: (str, str)
        :raise FileNotFoundError: If the definition file does not exists.
        :raise HTTPError: If the request failed.
        """
        with open(job_def, 'r', encoding='utf-8') as config:
            requests.post(
                url=f'{self.url}/createItem?name={name}',
                auth=credentials,
                headers={'Content-Type': 'application/xml'},
                data=config.read()
            ).raise_for_status()
