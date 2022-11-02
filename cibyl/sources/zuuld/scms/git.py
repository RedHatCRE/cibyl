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
from dataclasses import dataclass

from cibyl.sources.zuuld.errors import InvalidURL
from cibyl.sources.zuuld.scms.base import Storage
from kernel.tools.urls import is_git


@dataclass
class GitStorage(Storage):
    def __post_init__(self):
        if not is_git(self.url):
            raise InvalidURL(f"Not a Git URL: '{self.url}'")
