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

from cibyl.cli.parser import Parser
from cibyl.config import Config

LOG = logging.getLogger(__name__)


class Orchestrator:
    """This is a conceptual class representation of an app orchestrator.
    The purpose of the orchestrator is to run and coordinate the different
    phases of the application's lifecycle:

        1. Create initial parser
        2. Load the configuration
        3. Create the CI entities
        4. Update parser based on CI entities arguments
        5. Run query
        6. Print results

    :param config_file_path: the absolute path of the configuration file
    :type config_file_path: str, optional
    """

    def __init__(self, config_file_path=None):
        """Orchestrator constructor method"""
        self.config = Config(path=config_file_path)
        self.parser = Parser()

    def load_configuration(self):
        """Loads the configuration of the application."""
        self.config.load()

    @staticmethod
    def run_query():
        """Execute query based on provided arguments."""
        LOG.debug("running query...")
