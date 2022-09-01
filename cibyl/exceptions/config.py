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
from typing import Iterable, Tuple, Union

from cibyl.exceptions import CibylException
from cibyl.utils.colors import Colors

CONFIG_DOCS_URL = "https://cibyl.readthedocs.io/en/latest/configuration.html"
CHECK_DOCS_MSG = f"Check the documentation at {CONFIG_DOCS_URL} \
for more information"


class ConfigurationNotFound(CibylException):
    """Configuration file not found exception"""

    def __init__(self, paths: Union[Tuple[str], str]):
        if paths:
            paths = f" at: '{paths}'"
        else:
            paths = ""
        self.message = f"""Could not find configuration file{paths}.
{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class EmptyConfiguration(CibylException):
    """Configuration file is empty exception."""

    def __init__(self, file: str):
        self.message = f"""Configuration file {file} is empty.
{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class InvalidSourceConfiguration(CibylException):
    """Invalid source configuration exception."""

    def __init__(self, source_name: str, source_data: dict):
        self.message = f"""Invalid source configuration.

{source_name}: {source_data}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class NonSupportedSourceKey(CibylException):
    """Configuration section key is not supported."""

    def __init__(self, source_type: str, key: str):
        self.message = f"""The following key in "{source_type}" source type \
is not supported: {key}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class NonSupportedSystemKey(CibylException):
    """Configuration section key is not supported."""

    def __init__(self, system_type: str, key: str):
        self.message = f"""The following key in "{system_type}" system type \
is not supported: {key}\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class NonSupportedSourceType(CibylException):
    """Configuration source type is not supported."""

    def __init__(self, source_type: str, source_types: Iterable):
        types = Colors.blue("\n  ".join([t.value for t in source_types]))
        self.message = f"""The source type "{source_type}" isn't supported.
Use one of the following source types:\n  {types}"""

        super().__init__(self.message)


class MissingSourceKey(CibylException):
    """Configuration section is incomplete and missing a key."""

    def __init__(self, source_type: str, key: str):
        colored_key = Colors.blue(key)
        self.message = f"""The following key in "{source_type}" source type \
is missing and required for the source to become operational: {colored_key}"""

        super().__init__(self.message)


class MissingSystemKey(CibylException):
    """System configuration is incomplete and missing a key."""

    def __init__(self, system_name: str, key: str):
        colored_key = Colors.blue(key)
        self.message = f"""The following key in "{system_name}" system \
is missing and required for the system to become operational: {colored_key}"""

        super().__init__(self.message)


class MissingSourceType(CibylException):
    """Configuration source type isn't specified."""

    def __init__(self, source_name: str, source_types: Iterable):
        types = Colors.blue("\n  ".join([t.value for t in source_types]))
        self.message = f"""Missing 'driver: <TYPE>' for source {source_name}
Use one of the following source types:\n  {types}"""

        super().__init__(self.message)


class MissingSystemType(CibylException):
    """Configuration system type isn't specified."""

    def __init__(self, system_name: str, system_types: Iterable):
        types = Colors.blue("\n  ".join([t for t in system_types]))
        self.message = f"""Missing 'system_type: <TYPE>' for system {system_name}
Use one of the following system types:\n  {types}"""

        super().__init__(self.message)


class MissingSystemSources(CibylException):
    """Configuration system sources aren't specified."""

    def __init__(self, system_name: str):
        self.message = f"""Missing sources for system \
'{system_name}'

    environments:
        <ENVIRONMENT_NAME>:
            <SYSTEM_NAME>:
                sources:
                    driver: <SOURCE_TYPE>\n\n{CHECK_DOCS_MSG}"""

        super().__init__(self.message)


class MissingEnvironments(CibylException):
    """Configuration doesn't include any environments."""

    def __init__(self):
        self.message = f"""No environments defined in the configuration file. \

Configure environments with the "environments" mapping:

    environments:
        <ENVIRONMENT_NAME>\n\n{CHECK_DOCS_MSG}"""
        super().__init__(self.message)


class MissingSystems(CibylException):
    """An environment in the configuration doesn't include any systems."""

    def __init__(self, env_name: str):
        self.message = f"""No systems defined in the configuration file \
for the environment '{env_name}'

Configure systems by including them under the relevant environment name

    environments:
        <ENVIRONMENT_NAME>:
            <SYSTEM_NAME>\n\n{CHECK_DOCS_MSG}"""
        super().__init__(self.message)


class SchemaError(CibylException):
    def __init__(self, error: str):
        super().__init__(
            message=f'Configuration file found to be invalid due to error:\n'
                    f'\t- {error}\n'
                    f'\n'
                    f'{CHECK_DOCS_MSG}'
        )
