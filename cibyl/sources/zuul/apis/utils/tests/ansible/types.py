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
from typing import List, Optional

from cibyl.models.ci.zuul.tests.ansible import AnsibleTestStatus


@dataclass
class AnsibleTestHost:
    """Represents the result of an Ansible task when it got run on a host."""
    name: str
    """Name of the host."""
    action: str
    """Description of the task that was performed on the host."""
    result: AnsibleTestStatus = AnsibleTestStatus.UNKNOWN
    """Result of the task."""
    msg: Optional[str] = None
    """Additional information on the task result."""


@dataclass
class AnsibleTest:
    """Represents an Ansible task that got run as part of a build."""
    phase: str
    """Build phase when the task got executed. For example: 'Pre' or 'Run'."""
    name: str
    """Name of the task."""
    duration: float = 0
    """Time, in seconds, the task took to complete."""
    url: Optional[str] = None
    """Page where to find more info of the task's execution."""
    hosts: List[AnsibleTestHost] = field(default_factory=lambda: [])
    """Contains the results of the execution of the task on many hosts."""
