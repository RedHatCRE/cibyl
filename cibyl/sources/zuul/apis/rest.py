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
from urllib.parse import urljoin

from overrides import overrides
from requests import HTTPError, Session

from cibyl.sources.zuul.api import (ZuulAPI, ZuulAPIError, ZuulJobAPI,
                                    ZuulProjectAPI, ZuulTenantAPI)
from cibyl.utils.io import Closeable


class ZuulSession(Closeable):
    """Defines a link through which to communicate with the Zuul host.
    Communication is performed through the host's REST-API. This forms the
    base class for all communication with the host.
    """

    def __init__(self, session, host, verify):
        """Constructor.

        :param session: Low-level HTTP handler.
        :type session: :class:`Session`
        :param host: URL to the Zuul host.
        :type host: str
        :param verify: Indicates what is to be done regarding identification
            of the host. 'False' and 'None' disable need for validation.
            'True' activates it and leaves it up to the client's system to
            resolve it. A path to a certificate will use that file to
            identify the host.
        :type verify: str or bool or None
        """
        self._session = session
        self._session.verify = verify

        if not host.endswith('/'):
            host += '/'

        self._host = host

    @property
    def host(self):
        return self._host

    @property
    def api(self):
        """
        :return: URL to the entry point of the host's REST-API.
        :rtype: str
        """
        return urljoin(self.host, 'api/')

    def get(self, service):
        """Performs a GET action on one of the host's end-points.

        :param service: Name of the end-point to be attacked.
        :type service: str
        :return: JSON-like response from host.
        :rtype: dict
        :raises ZuulAPIError: If the request failed.
        """
        request = self._session.get(urljoin(self.api, service))

        self._check_request_status(request)

        return request.json()

    @overrides
    def close(self):
        self._session.close()

    @staticmethod
    def _check_request_status(request):
        try:
            request.raise_for_status()
        except HTTPError as ex:
            code = request.status_code

            if code == 401:
                raise ZuulAPIError('Unauthorized.') from ex

            if code == 403:
                raise ZuulAPIError('Insufficient privileges.') from ex

            if code == 404:
                raise ZuulAPIError('Resource not found.') from ex

            raise ZuulAPIError(f'Unknown error code {code}') from ex


class ZuulJobRESTClient(ZuulJobAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session, tenant, job):
        """Constructor. See parent class for more information.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(tenant, job)

        self._session = session

    def __eq__(self, other):
        if not issubclass(type(other), ZuulJobAPI):
            return False

        if self is other:
            return True

        return self.tenant == other.tenant and self.name == other.name

    @property
    def url(self):
        base = self._session.host[:-1]
        tenant = self.tenant

        return f"{base}/t/{tenant.name}/job/{self.name}"

    def builds(self):
        return self._session.get(
            f'tenant/{self.tenant.name}/builds?job_name={self.name}'
        )

    @overrides
    def close(self):
        self._session.close()


class ZuulProjectRESTClient(ZuulProjectAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session, tenant, project):
        """Constructor. See parent class for more information.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(tenant, project)

        self._session = session

    def __eq__(self, other):
        if not issubclass(type(other), ZuulProjectAPI):
            return False

        if self is other:
            return True

        return self.tenant == other.tenant and self.name == other.name

    @property
    def url(self):
        base = self._session.host[:-1]
        tenant = self.tenant

        return f"{base}/t/{tenant.name}/project/{self.name}"

    @overrides
    def close(self):
        self._session.close()


class ZuulTenantRESTClient(ZuulTenantAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session, tenant):
        """Constructor. See parent class for more information.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(tenant)

        self._session = session

    def builds(self):
        return self._session.get(f'tenant/{self.name}/builds')

    def buildsets(self):
        return self._session.get(f'tenant/{self.name}/buildsets')

    def projects(self):
        result = []

        for project in self._session.get(f'tenant/{self.name}/projects'):
            result.append(ZuulProjectRESTClient(self._session, self, project))

        return result

    def jobs(self):
        result = []

        for job in self._session.get(f'tenant/{self.name}/jobs'):
            result.append(ZuulJobRESTClient(self._session, self, job))

        return result

    @overrides
    def close(self):
        self._session.close()


class ZuulRESTClient(ZuulAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session):
        """ Constructor.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        self._session = session

    @staticmethod
    def from_url(host, cert=None):
        """Builds a client through the parameters that define a session.

        :param host: URL to the host to be targeted.
        :type host: str
        :param cert: Path to certificate to be used to validate the host.
            Recommended usage in production environments as otherwise
            the session would be vulnerable to man-in-the-middle attacks.
            'None' removes all need for validation.
        :type cert: str or None
        :return: A client instance.
        :rtype: :class:`ZuulRESTClient`
        """
        return ZuulRESTClient(ZuulSession(Session(), host, cert))

    def info(self):
        return self._session.get('info')

    def tenants(self):
        result = []

        for tenant in self._session.get('tenants'):
            result.append(ZuulTenantRESTClient(self._session, tenant))

        return result

    @overrides
    def close(self):
        self._session.close()
