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
class AnsibleHost:
    name: str
    action: str
    result: AnsibleTestStatus = AnsibleTestStatus.UNKNOWN
    msg: Optional[str] = None


@dataclass
class AnsibleTest:
    phase: str
    name: str
    duration: float = 0
    url: Optional[str] = None
    hosts: List[AnsibleHost] = field(default_factory=lambda: [])
