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
from abc import ABC
from typing import Optional, Union
from urllib.parse import urljoin

from overrides import overrides
from requests import HTTPError, Session

from cibyl.sources.zuul.apis import ZuulAPIError, ZuulBuildAPI
from cibyl.utils.io import Closeable


class ZuulSession(Closeable):
    """Defines a link through which to communicate with the Zuul host.
    Communication is performed through the host's REST-API. This forms the
    base class for all communication with the host.
    """

    def __init__(
        self,
        session: Session,
        host: str,
        verify: Optional[Union[bool, str]]
    ):
        """Constructor.

        :param session: Low-level HTTP handler.
        :param host: URL to the Zuul host.
        :param verify: Indicates what is to be done regarding identification
            of the host. 'False' and 'None' disable need for validation.
            'True' activates it and leaves it up to the client's system to
            resolve it. A path to a certificate will use that file to
            identify the host.
        """
        self._session = session
        self._session.verify = verify

        if not host.endswith('/'):
            host += '/'

        self._host = host

    @property
    def session(self):
        """
        :return: The low-level session this uses to perform requests.
        :rtype: :class:`Session`
        """
        return self._session

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
                msg = f"Error - 401. " \
                      f"Unauthorized access to resource: '{request.url}'. " \
                      f"Check credentials and try again."

                raise ZuulAPIError(msg) from ex

            if code == 403:
                msg = f"Error - 403. " \
                      f"Insufficient privileges " \
                      f"to access resource at: '{request.url}'. " \
                      f"Check credentials and try again."

                raise ZuulAPIError(msg) from ex

            if code == 404:
                msg = f"Error - 404. " \
                      f"Resource not found at: '{request.url}'. " \
                      f"Check resource availability and try again."

                raise ZuulAPIError(msg) from ex

            msg = f"Unknown error code: '{code}' " \
                  f"returned by host at: {request.url}. " \
                  f"Wait for a couple of minutes and try again..."

            raise ZuulAPIError(msg) from ex


class ZuulHTTPBuildAPI(ZuulBuildAPI, ABC):
    """Branch of build APIs based around the usage of an HTTP service.
    """

    def __init__(self, session, job, build):
        """Constructor. See parent for more information.

        :param session: The link through which the HTTP service will be
            contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(job, build)

        self._session = session

    @property
    def session(self):
        return self._session
