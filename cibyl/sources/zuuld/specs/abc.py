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
from dataclasses import dataclass, field
from pathlib import Path

from kernel.tools.urls import URL


@dataclass
class SCMSpec:
    """Defines location of Zuul.D files for a generic SCM.
    """
    remote: URL
    """Address to the repository that hosts the files."""
    directory: Path = field(default_factory=lambda: Path('zuul.d/'))
    """Path, relative to the repository's root, to the directory where the
    Zuul.D files are stored in.
    """

    def __str__(self):
        return f"[Remote: '{self.remote}', Directory: '{self.directory}']"
