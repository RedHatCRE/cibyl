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
from typing import Any, Dict, Iterable, Optional


@dataclass
class Job:
    """Transcription of a job object from a Zuul.D file.
    """
    name: str
    """Name of the job."""
    parent: Optional[str] = field(default_factory=lambda: None)
    """Name of the parent job for this one."""
    branches: Iterable[str] = field(default_factory=lambda: [])
    """Branches the job triggers at."""
    vars: Dict[str, Any] = field(default_factory=lambda: {})
    """Collection of variables that specialize the job."""
