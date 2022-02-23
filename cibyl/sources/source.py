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
import logging

from cibyl.models.ci.system import System

LOG = logging.getLogger(__name__)


class Source:
    """Represents a source of a system on which queries are performed."""

    def __init__(self, name: str, url: str = None):
        self.name = name
        self.url = url

    def query(self, system: System,  args):
        """Performs query on the source and populates environment instance"""
        LOG.info("performing query on %s", self.name)

    def connect(self):
        """Creates a client and initiates a connection to the source."""
        LOG.info("connection initiated: %s", self.name)
