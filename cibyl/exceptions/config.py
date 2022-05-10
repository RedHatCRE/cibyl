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
from cibyl.exceptions import CibylException

CONFIG_DOCS_URL = "https://cibyl.readthedocs.io/en/latest/configuration.html"


class InvalidConfiguration(CibylException):
    """Invalid configuration exception"""

    def __init__(self, message="""
Invalid Configuration.
A valid configuration should specify an environment, its system(s) and the
system(s) details

environments:
    env_1:
        jenkins_system:
            system_type: jenkins"""):
        self.message = message
        super().__init__(self.message)


class ConfigurationNotFound(CibylException):
    """Configuration file not found exception"""

    def __init__(self, paths):
        if paths:
            paths = f" at: {paths}"
        else:
            paths = ""
        self.message = f"""Could not find configuration file{paths}.\n
Check the documentation at {CONFIG_DOCS_URL} for more information"""

        super().__init__(self.message)


class EmptyConfiguration(CibylException):
    """Configuration file is empty exception."""

    def __init__(self, file):
        self.message = f"""Configuration file {file} is empty.\n
Check the documentation at {CONFIG_DOCS_URL} for more \
details about the configuration syntax."""

        super().__init__(self.message)


class InvalidSourceConfiguration(CibylException):
    """Invalid source configuration exception."""

    def __init__(self, source_name, source_data):
        self.message = f"""Invalid source configuration.

{source_name}: {source_data}

Check the documentation at {CONFIG_DOCS_URL} for more information"""

        super().__init__(self.message)
