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
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source

import logging

import jenkins


class Jenkins(Source):
    """A class representation of Jenkins client."""

    def __init__(self, url, username, token):
        self.client = jenkins.Jenkins(url, username=username, token=token)

    def get_jobs(self):
        return self.client.get_all_jobs(folder_depth=None)

    def populate_jobs(self, system, jobs):
        for job in jobs:
            system.jobs.append(Job(name=job.get('name')))

    def query(system, args):
        LOG.debug("querying system {} using source: {}".format(
            system.name.value, self.__name__))

        if args.get('jobs'):
            jobs = self.get_jobs()
            Source.populate_jobs(jobs)

        if all([argument.populated for arg in args]):
            return system


class JenkinsOSP(Jenkins):
    """A class representation of OSP Jenkins client."""

    def __init__(self, url, username, token):
        super(self, JenkinsOSP).__init__(url, username, token)
