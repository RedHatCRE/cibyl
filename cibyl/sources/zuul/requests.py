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
from abc import ABC, abstractmethod

from cibyl.utils.filtering import apply_filters


class Request(ABC):
    def __init__(self):
        self._filters = []

    @abstractmethod
    def get(self):
        raise NotImplementedError


class TenantsRequest(Request):
    def __init__(self, zuul):
        super().__init__()

        self._zuul = zuul

    def get(self):
        tenants = apply_filters(self._zuul.tenants(), *self._filters)

        return [TenantResponse(tenant) for tenant in tenants]


class JobsRequest(Request):
    def __init__(self, tenant):
        super().__init__()

        self._tenant = tenant

    def with_name(self, *name):
        self._filters.append(lambda job: job.name in name)
        return self

    def with_url(self, *url):
        self._filters.append(lambda job: job.url in url)
        return self

    def get(self):
        jobs = apply_filters(self._tenant.jobs(), *self._filters)

        return [JobResponse(self._tenant, job) for job in jobs]


class BuildsRequest(Request):
    def __init__(self, job):
        super().__init__()

        self._job = job
        self._last_build_only = False

    def with_uuid(self, *uuid):
        self._filters.append(lambda build: build['uuid'] in uuid)
        return self

    def with_status(self, *status):
        self._filters.append(lambda build: build['result'] in status)
        return self

    def with_last_build_only(self):
        # This one needs to be applied after all the other filters.
        self._last_build_only = True
        return self

    def get(self):
        builds = apply_filters(self._job.builds(), *self._filters)

        # Perform special filters
        if self._last_build_only:
            builds = builds[0:1]  # Just the newest build

        return [BuildResponse(self._job, build) for build in builds]


class TenantResponse:
    def __init__(self, tenant):
        self._tenant = tenant

    @property
    def name(self):
        return self._tenant.name

    def jobs(self):
        return JobsRequest(self._tenant)


class JobResponse:
    def __init__(self, tenant, job):
        self._tenant = tenant
        self._job = job

    @property
    def tenant(self):
        return self._tenant

    @property
    def name(self):
        return self._job.name

    @property
    def url(self):
        return self._job.url

    def builds(self):
        return BuildsRequest(self._job)


class BuildResponse:
    def __init__(self, job, build):
        self._job = job
        self._build = build

    @property
    def job(self):
        return self._job

    @property
    def data(self):
        return self._build
