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


class ZuulAPIError(Exception):
    """Represents an error occurring while performing a call to Zuul's API
    """


class ZuulTenantAPI(ABC):
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
        """
        return self._tenant['name']

    @abstractmethod
    def builds(self):
        """A build is an instance of a job running independently.

        :return: Information about all executed builds under this tenant.
        :rtype: list[dict]
        """
        raise NotImplementedError

    @abstractmethod
    def buildsets(self):
        """A buildset is a collection of builds running under a common context.

        :return: Information about all executed buildsets under this tenant.
        :rtype: list[dict]
        """
        raise NotImplementedError

    @abstractmethod
    def jobs(self):
        """A job describes the steps that need to be taken in order to test
        a project.

        :return: Information about all jobs under this tenant.
        :rtype: list[dict]
        """
        raise NotImplementedError


class ZuulAPI(ABC):
    """Interface describing the actions that can be taken over Zuul's API.
    """

    @abstractmethod
    def info(self):
        """Information which define the target host. Among this info there
        are entries such as 'capabilities' or 'authentication' param.

        :return: General information about the host.
        :rtype: dict
        """
        raise NotImplementedError

    @abstractmethod
    def tenants(self):
        """Gets all tenants currently present on the host.

        :return: A sub-api to retrieve information about all tenants on the
            host.
        :rtype: list[:class:`ZuulTenantAPI`]
        """
        raise NotImplementedError
