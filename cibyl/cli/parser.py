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
import argparse
import logging

LOG = logging.getLogger(__name__)


class Parser:
    """This is a conceptual class representation of an app parser.
    The parser created as basic argparse based parser and later it's
    extended with arguments collected from the different CI models'
    attributes.
    """

    def __init__(self):
        self.argument_parser = argparse.ArgumentParser()
        self.__add_arguments()

    def __add_arguments(self) -> None:
        """Creates argparse parser with all its sub-parsers."""
        self.argument_parser.add_argument(
            '--debug', '-d', action='store_true',
            dest="debug", help='turn on debug')
        self.argument_parser.add_argument(
            '--config', '-c', dest="config_file_path")
        self.argument_parser.add_argument(
            '--plugin', '-p', dest="plugin", default="openstack")

    def parse(self):
        """Parses arguments"""
        # First item is the namespace of the parsed known arguments
        return self.argument_parser.parse_known_args()[0]

    @staticmethod
    def extend(ci_environments):
        """Extends parser with arguments based from the given
        CI environment entities.
        """
        for env in ci_environments:
            LOG.debug("extending arguments from env %s", env.name.value)
