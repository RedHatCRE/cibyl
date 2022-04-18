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
import os
from tempfile import TemporaryDirectory

from git import Repo
from overrides import overrides

from tests.e2e.containers import ComposedContainer, wait_for


class OpenDevZuulContainer(ComposedContainer):
    def __init__(self):
        # Download dockerfile from OpenDev
        self._repo = TemporaryDirectory()

        Repo.clone_from('https://opendev.org/zuul/zuul', self.repo)

        # Point to dockerfile in repo
        super().__init__(
            filedir=os.path.join(self.repo, 'doc/source/examples'),
            filename='docker-compose.yaml'
        )

    @property
    def url(self):
        # Defined in dockerfile
        return 'http://localhost:9000'

    @property
    def repo(self):
        return self._repo.name

    @overrides
    def _wait_until_ready(self):
        wait_for(f'{self.url}/api')

    @overrides
    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._repo.cleanup()
