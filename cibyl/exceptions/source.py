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
from cibyl.utils.colors import Colors


class NoSupportedSourcesFound(CibylException):
    """Exception for a case where non of the sources of a single system is
       implementing the function of the argument the user is interested in
    """

    def __init__(self, system: str, function: str):
        self.message = f"""Couldn't find any enabled source for the system
{system} that implements the function {function}.""".replace("\n", " ")
        super().__init__(self.message)


class NoValidSources(CibylException):
    """Exception for a case when no valid source is found."""

    def __init__(self, system: str = "", sources: str = ""):
        if sources:
            sources = Colors.blue('\n  '.join(sources))
            sources = f"\nAvailable sources:\n  {sources}"
        if system:
            system = f" defined for the system {system.name.value}"
        self.message = f"""No valid source found{system}.

Define sources for the system with the "sources" mapping

  <ENVIRONMENT_NAME>:
      <SYSTEM_NAME>:
          sources:
              <SOURCE_NAME>{sources}"""

        super().__init__(self.message)


class SourceException(CibylException):
    """Abstract exception to representation any error while querying a
    source."""


class MissingArgument(SourceException):
    """Represents a missing required argument inside a source method call."""

    def __init__(self, message: str = 'Missing required argument.'):
        """Constructor.
        """
        super().__init__(message)


class InvalidArgument(SourceException):
    """Represents an invalid combination of arguments inside a source
    method call."""

    def __init__(self, message: str = 'Invalid argument passed.'):
        """Constructor.
        """
        super().__init__(message)
