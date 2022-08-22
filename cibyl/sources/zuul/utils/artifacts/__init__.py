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
from enum import Enum

from cibyl.exceptions.source import SourceException


class ArtifactError(SourceException):
    """An error occurring during retrieval of a Zuul build artifact.
    """


class ArtifactKind(Enum):
    """Represents all known types of artifacts.
    """
    OTHER = 0
    """Type unknown, treat as generic."""
    ZUUL_MANIFEST = 1
    """Artifact is a manifest, which gives information on the log files
    resulted from the build's execution."""

    @staticmethod
    def from_string(string):
        """Gets the artifact type from a string.

        Known strings:
            - 'zuul_manifest' -> :attr:`ArtifactKind.ZUUL_MANIFEST`

        Any other string will return :attr:`ArtifactKind.OTHER`.

        :param string: Text to parse.
        :type string: str
        :return: Type inferred through the text.
        :rtype: :class:`ArtifactKind`
        """
        if string == 'zuul_manifest':
            return ArtifactKind.ZUUL_MANIFEST

        return ArtifactKind.OTHER


class Artifact:
    """Represents an artifact published by a build.
    """
    name: str = 'Unknown'
    """Name of the artifact."""
    url: str = 'Unknown'
    """URL where its contents are located."""
    kind: ArtifactKind = ArtifactKind.OTHER
    """The type of artifact."""
