"""Provides higher-level requests for the retrieval of data from Zuul. The
requests provided here abstract how the data is queried and focuses only on
its access and filtering. You may consider this module the interface between a
Zuul host and a Zuul source.

License:
#
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
#
"""
from abc import ABC

from cibyl.utils.filtering import apply_filters


class Request(ABC):
    """Base class for any kind of request.
    """

    def __init__(self):
        """Constructor.
        """
        self._filters = []


class TenantsRequest(Request):
    """High-Level petition focused on retrieval of data related to tenants.
    """

    def __init__(self, zuul):
        """Constructor.

        :param zuul: Low-Level Zuul API.
        :type zuul: :class:`cibyl.sources.zuul.api.ZuulAPI`
        """
        super().__init__()

        self._zuul = zuul

    def with_name(self, *name):
        """Will limit request to tenants with a certain name.

        :param name: Name of the desired tenant.
        :return: The request's instance.
        :rtype: :class:`TenantsRequest`
        """
        self._filters.append(lambda tenant: tenant.name in name)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: :class:`TenantResponse`
        """
        tenants = apply_filters(self._zuul.tenants(), *self._filters)

        return [TenantResponse(tenant) for tenant in tenants]


class ProjectsRequest(Request):
    """High-Level petition focused on retrieval of data related to projects.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Low-Level API to access this job's tenant.
        :type tenant: :class:`cibyl.sources.zuul.api.ZuulTenantAPI`
        """
        super().__init__()

        self._tenant = tenant

    def with_name(self, *name):
        """Will limit request to projects with a certain name.

        :param name: Name of the desired project.
        :type name: str
        :return: The request's instance.
        :rtype: :class:`ProjectRequest`
        """
        self._filters.append(lambda project: project.name in name)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: :class:`ProjectResponse`
        """
        projects = apply_filters(self._tenant.projects(), *self._filters)

        return [ProjectResponse(self._tenant, project) for project in projects]


class JobsRequest(Request):
    """High-Level petition focused on retrieval of data related to jobs.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Low-Level API to access this job's tenant.
        :type tenant: :class:`cibyl.sources.zuul.api.ZuulTenantAPI`
        """
        super().__init__()

        self._tenant = tenant

    def with_name(self, *name):
        """Will limit request to jobs with a certain name.

        :param name: Name of the desired job.
        :type name: str
        :return: The request's instance.
        :rtype: :class:`JobsRequest`
        """
        self._filters.append(lambda job: job.name in name)
        return self

    def with_url(self, *url):
        """Will limit request to jobs at a certain URL.

        :param url: URL of the desired job.
        :type url: str
        :return: The request's instance.
        :rtype: :class:`JobsRequest`
        """
        self._filters.append(lambda job: job.url in url)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: :class:`JobResponse`
        """
        jobs = apply_filters(self._tenant.jobs(), *self._filters)

        return [JobResponse(self._tenant, job) for job in jobs]


class BuildsRequest(Request):
    """High-Level petition focused on retrieval of data related to builds.
    """

    def __init__(self, job):
        """Constructor.

        :param job: Low-Level API to access this build's job.
        :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
        """
        super().__init__()

        self._job = job
        self._last_build_only = False

    def with_uuid(self, *uuid):
        """Will limit request to builds with a certain ID.

        :param uuid: ID of the desired build.
        :type uuid: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """
        self._filters.append(lambda build: build['uuid'] in uuid)
        return self

    def with_status(self, *status):
        """Will limit request to builds with a certain status.

        :param status: Status of the desired build.
        :type status: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """
        self._filters.append(lambda build: build['result'] in status)
        return self

    def with_last_build_only(self):
        """Will only return the latest build that meets the filters.

        :return: The request's instance.
        :rtype: :class:`BuildRequest`
        """
        # This one needs to be applied after all the other filters.
        self._last_build_only = True
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: :class:`BuildsResponse`
        """
        builds = apply_filters(self._job.builds(), *self._filters)

        # Perform special filters
        if self._last_build_only:
            builds = builds[0:1]  # Just the newest build

        return [BuildResponse(self._job, build) for build in builds]


class TenantResponse:
    """Response for a :class:`TenantsRequest`.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Low-Level API to access the tenant's data.
        :type tenant: :class:`cibyl.sources.zuul.api.ZuulTenantAPI`
        """
        self._tenant = tenant

    @property
    def name(self):
        """
        :return: Name of the tenant.
        :rtype: str
        """
        return self._tenant.name

    def projects(self):
        """
        :return: A request for this tenant's projects.
        :rtype: :class:`ProjectsRequest`
        """
        return ProjectsRequest(self._tenant)

    def jobs(self):
        """
        :return: A request for this tenant's jobs.
        :rtype: :class:`JobsRequest`
        """
        return JobsRequest(self._tenant)


class ProjectResponse:
    """Response for :class:`ProjectsRequest`.
    """

    def __init__(self, tenant, project):
        """Constructor.

        :param tenant: Low-Level API to access this project's tenant.
        :type tenant: :class:`cibyl.sources.zuul.api.ZuulTenantAPI`
        :param project: Low-Level API to access the project's data.
        :type project: :class:`cibyl.sources.zuul.api.ZuulProjectAPI`
        """
        self._tenant = tenant
        self._project = project

    @property
    def tenant(self):
        """
        :return: Response to this project's tenant.
        :rtype: :class:`TenantResponse`
        """
        return TenantResponse(self._tenant)

    @property
    def name(self):
        """
        :return: The project's name.
        :rtype: str
        """
        return self._project.name


class JobResponse:
    """Response for a :class:`JobsRequest`.
    """

    def __init__(self, tenant, job):
        """Constructor.

        :param tenant: Low-Level API to access this job's tenant.
        :type tenant: :class:`cibyl.sources.zuul.api.ZuulTenantAPI`
        :param job: Low-Level API to access the job's data.
        :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
        """
        self._tenant = tenant
        self._job = job

    @property
    def tenant(self):
        """
        :return: Response to this job's tenant.
        :rtype: :class:`TenantResponse`
        """
        return TenantResponse(self._tenant)

    @property
    def name(self):
        """
        :return: The job's name.
        :rtype: str
        """
        return self._job.name

    @property
    def url(self):
        """
        :return: The job's URL.
        :rtype: str
        """
        return self._job.url

    def builds(self):
        """
        :return: A request to this job's builds.
        :rtype: :class:`BuildsRequest`
        """
        return BuildsRequest(self._job)


class BuildResponse:
    """Response for a :class:`BuildsRequest`.
    """

    def __init__(self, job, build):
        """Constructor.

        :param job: Low-Level API to access this build's job.
        :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
        :param build: Raw data for this build.
        :type build: dict[str, Any]
        """
        self._job = job
        self._build = build

    @property
    def job(self):
        """
        :return: Response for this build's job.
        :rtype: :class:`JobResponse`
        """
        return JobResponse(self._job.tenant, self._job)

    @property
    def data(self):
        """
        :return: Raw data of this build.
        :rtype: dict[str, Any]
        """
        return self._build
