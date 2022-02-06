# Copyright 2022 Red Hat
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
import crayons
import logging
import os
import sys
import yaml

LOG = logging.getLogger(__name__)


class Config(object):

    DEFAULT_RELATIVE_PATH = '.cibyl/cibyl.yaml'
    DEFAULT_FILE_PATH = os.path.join(
        os.path.expanduser("~"), DEFAULT_RELATIVE_PATH)

    def __init__(self, file_path=DEFAULT_FILE_PATH, data={}):
        self.file_path = file_path
        self.data = data

    def load(self):
        LOG.debug("{}: {}".format(
            crayons.yellow("loading conf"), self.file_path))
        try:
            with open(self.file_path, 'r') as stream:
                self.data = yaml.safe_load(stream) or {}
            return self.data
        except FileNotFoundError:
            LOG.error(
                "couldn't find configuration file :'(\n{}".format(
                    crayons.red(self.file_path)))
            sys.exit(2)

    @staticmethod
    def get_config_file_path(arguments):
        """ Manually parse user arguments and check if config
            argument was used. If yes, use the value provided.
            If not, use default from Config class

        Args:
            arguments: list of arguments
        Returns:
            A string which is the config file path
        """
        config_file_path = Config.DEFAULT_FILE_PATH
        for i, item in enumerate(arguments[1:]):
            if item == "--config":
                config_file_path = arguments[i+2]
        return config_file_path
