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

from tests.cibyl.e2e.containers import ComposedContainer, wait_for


class OpenDevZuulContainer(ComposedContainer):
    def __init__(self):
        # Download dockerfile from OpenDev
        self._workspace = TemporaryDirectory()

        Repo.clone_from(self.origin, self.workspace)

        # Point to dockerfile in repo
        super().__init__(
            filedir=os.path.join(self.workspace, 'doc/source/examples'),
            filename='docker-compose.yaml'
        )

    @property
    def host(self):
        # Defined in dockerfile
        return 'http://localhost:9000'

    @property
    def origin(self):
        return 'https://github.com/rhos-infra/cibyl-e2e-zuul.git'

    @property
    def workspace(self):
        return self._workspace.name

    @overrides
    def _wait_until_ready(self):
        wait_for(f'{self.host}/api')

    @overrides
    def stop(self):
        super().stop()
        self._workspace.cleanup()
