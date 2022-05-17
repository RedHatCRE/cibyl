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
CHECK_DOCS_MSG = f"Check the documentation at {CONFIG_DOCS_URL} \
for more information"


class InvalidConfiguration(CibylException):
    """Invalid configuration exception"""

    def __init__(self):
        self.message = f"""Invalid Configuration.
A valid configuration should specify an environment, its system(s) and at \
least one source for each system.\n\n{CHECK_DOCS_MSG}"""
        super().__init__(self.message)


class ConfigurationNotFound(CibylException):
    """Configuration file not found exception"""

    def __init__(self, paths):
        if paths:
            paths = f" at: '{paths}'"
        else:
            paths = ""
        self.message = f"""Could not find configuration file{paths}.
{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class EmptyConfiguration(CibylException):
    """Configuration file is empty exception."""

    def __init__(self, file):
        self.message = f"""Configuration file {file} is empty.
{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class InvalidSourceConfiguration(CibylException):
    """Invalid source configuration exception."""

    def __init__(self, source_name, source_data):
        self.message = f"""Invalid source configuration.

{source_name}: {source_data}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class NonSupportedSourceKey(CibylException):
    """Configuration section key is not supported."""

    def __init__(self, source_type, key):
        self.message = f"""The following key in "{source_type}" source type \
is not supported: {key}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class NonSupportedSystemKey(CibylException):
    """Configuration section key is not supported."""

    def __init__(self, source_type, key):
        self.message = f"""The following key in "{source_type}" system type \
is not supported: {key}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)
