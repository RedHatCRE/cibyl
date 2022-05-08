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

from cibyl.sources.source import Source, speed_index
from cibyl.sources.zuuld.git_api import ZuulGitHub, ZuulLocal


class ZuulD(Source):
    def __init__(self, name: str, driver: str, **kwargs):
        super().__init__(name, driver, **kwargs)
        self.repos = kwargs.get("repos")
        self.kwargs = kwargs
        remote = kwargs.get("remote", False)
        if not remote:
            self.api = ZuulLocal(self.kwargs)
        else:
            self.api = ZuulGitHub(self.kwargs)

    def setup(self):
        """
        Setup ZuulD source
        """
        self.api._validate()

    @speed_index({'base': 3})
    def get_jobs(self, **kwargs):
        """
        ZuulD source get_jobs method
        """
        return self.api.get_jobs()
