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
import logging

from cibyl.sources.zuul.api import ZuulAPIError

LOG = logging.getLogger(__name__)


class ZuulClientError(Exception):
    """Represents any error coming out of actions performed by the Zuul client.
    """


class ZuulClient:  # pylint: disable=too-few-public-methods
    """High-Level Zuul client meant to simplify retrieval of data and
    execution of commands over the host.
    """

    def __init__(self, api):
        """Constructor.

        :param api: The low-level client this will use to communicate
            with Zuul.
        :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
        """
        self._api = api

    def connect(self):
        """Verifies that connection with the Zuul host can be made.

        :raises ZuulClientError: If connection to Zuul failed.
        """
        try:
            self._api.info()
        except ZuulAPIError as ex:
            raise ZuulClientError(
                f"Unable to connect to Zuul host at: '{self._api.url}'."
            ) from ex

        LOG.info("Connected to Zuul host at: '%s'.", self._api.url)
