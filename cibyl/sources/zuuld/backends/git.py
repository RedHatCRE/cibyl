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
from typing import Iterable

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import ZuulDBackend, T
from cibyl.sources.zuuld.models import Job
from cibyl.sources.zuuld.specs.git import GitSpec


class GitBackend(ZuulDBackend[GitSpec]):
    class Get(ZuulDBackend.Get):
        @overrides
        def jobs(self, spec: T) -> Iterable[Job]:
            return []

    def __init__(self):
        super().__init__(get=GitBackend.Get())
