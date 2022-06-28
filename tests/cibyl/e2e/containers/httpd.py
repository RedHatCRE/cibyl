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
from overrides import overrides

from tests.cibyl.e2e.containers import ComposedContainer, wait_for


class HTTPDContainer(ComposedContainer):
    """Meant for tests that verify Cibyl's behaviour against an HTTP host.
    """

    def __init__(self):
        super().__init__('tests/cibyl/e2e/data/images/httpd')

    @property
    def url(self):
        # Obtained from the 'docker-compose' definition
        return 'http://172.19.1.1:80/'

    @overrides
    def _wait_until_ready(self):
        # The definition indicates that the server is exposed on port 8080.
        wait_for('http://localhost:8080/')
