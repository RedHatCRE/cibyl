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

from cibyl.exceptions.source import SourceException
from cibyl.sources.zuul.providers import JobsProvider, PipelinesProvider
from cibyl.utils.io import Closeable


class ZuulAPIError(SourceException):
    """Represents an error occurring while performing a call to Zuul's API
    """


class ZuulJobAPI(Closeable, ABC):
    """Interface which defines the information that can be retrieved from
    Zuul regarding a particular job.
    """

    def __init__(self, tenant, job):
        """Constructor.

        :param tenant: Tenant this job belongs to.
        :type tenant: :class:`ZuulTenantAPI`
        :param job: Description of the job being consulted by this
            API. At least a field called 'name' providing the name
            of the job is required here.
        :type job: dict
        """
        self._tenant = tenant
        self._job = job

    @property
    def tenant(self):
        """
        :return: The tenant this job belongs to.
        :rtype: :class:`ZuulTenantAPI`
        """
        return self._tenant

    @property
    def name(self):
        """
        :return: Name of the job being consulted.
        :rtype: str
        """
        return self._job['name']

    @property
    @abstractmethod
    def url(self):
        """
        :return: URL where this job can be consulted at.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def builds(self):
        """
        :return: The builds of this job.
        :rtype: list[dict]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError


class ZuulPipelineAPI(Closeable, JobsProvider, ABC):
    def __init__(self, project, pipeline):
        self._project = project
        self._pipeline = pipeline

    @property
    def project(self):
        return self._project

    @property
    def name(self):
        return self._pipeline['name']

    @abstractmethod
    def jobs(self):
        raise NotImplementedError


class ZuulProjectAPI(Closeable, PipelinesProvider, ABC):
    """Interface which defines the information that can be retrieved from
    Zuul regarding a particular project.
    """

    def __init__(self, tenant, project):
        """Constructor.

        :param tenant: Tenant this job belongs to.
        :type tenant: :class:`ZuulTenantAPI`
        :param project.: Description of the project being consulted by this
            API. At least a field called 'name' providing the name
            of the project is required here.
        :type project: dict
        """
        self._tenant = tenant
        self._project = project

    @property
    def tenant(self):
        """
        :return: The tenant this project belongs to.
        :rtype: :class:`ZuulTenantAPI`
        """
        return self._tenant

    @property
    def name(self):
        """
        :return: Name of the project being consulted.
        :rtype: str
        """
        return self._project['name']

    @property
    @abstractmethod
    def url(self):
        """
        :return: URL where this project can be consulted at.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def pipelines(self):
        raise NotImplementedError


class ZuulTenantAPI(Closeable, JobsProvider, ABC):
    """Interface which defines the information that can be retrieved from
    Zuul regarding a particular tenant.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Description of the tenant being consulted by this
            API. At least a field called 'name' providing the name
            of the tenant is required here.
        :type tenant: dict
        """
        self._tenant = tenant

    @property
    def name(self):
        """
        :return: Name of the tenant being consulted.
        :rtype: str
        """
        return self._tenant['name']

    @abstractmethod
    def builds(self):
        """A build is an instance of a job running independently.

        :return: Information about all executed builds under this tenant.
        :rtype: list[dict]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError

    @abstractmethod
    def buildsets(self):
        """A buildset is a collection of builds running under a common context.

        :return: Information about all executed buildsets under this tenant.
        :rtype: list[dict]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError

    @abstractmethod
    def projects(self):
        """A project is the representation of a source code that Zuul is
        meant to interact with.

        :return: Information about all projects under this tenant.
        :rtype: list[:class:`ZuulProjectAPI`]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError

    @abstractmethod
    def jobs(self):
        """A job describes the steps that need to be taken in order to test
        a project.

        :return: Information about all jobs under this tenant.
        :rtype: list[:class:`ZuulJobAPI`]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError


class ZuulAPI(Closeable, ABC):
    """Interface describing the actions that can be taken over Zuul's API.
    """

    @abstractmethod
    def info(self):
        """Information which define the target host. Among this info there
        are entries such as 'capabilities' or 'authentication' param.

        :return: General information about the host.
        :rtype: dict
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError

    @abstractmethod
    def tenants(self):
        """Gets all tenants currently present on the host.

        :return: A sub-api to retrieve information about all tenants on the
            host.
        :rtype: list[:class:`ZuulTenantAPI`]
        :raises ZuulAPIError: If the request failed.
        """
        raise NotImplementedError
