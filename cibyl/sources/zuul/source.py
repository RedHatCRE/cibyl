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

from cibyl.models.attribute import AttributeDictValue
from cibyl.sources.source import Source, speed_index
from cibyl.sources.zuul.apis.rest import ZuulRESTClient
from cibyl.sources.zuul.query import handle_query


class Zuul(Source):
    """Source implementation for a Zuul host.
    """

    def __init__(self, api, name, driver, url, **kwargs):
        """Constructor.

        :param api: Medium of communication with host.
        :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
        :param name: Name of the source.
        :type name: str
        :param driver: Driver used by the source.
        :type driver: str
        :param url: Address where the host is located.
        :type url: str
        :param kwargs: Additional parameters that define the source.
        :type kwargs: Any
        """
        # URLs are built assuming no slash at the end of URL
        if url.endswith('/'):
            url = url[:-1]  # Removes last character of string

        super().__init__(name, driver, url=url, **kwargs)

        self._api = api

    @staticmethod
    def new_source(url, cert=None, **kwargs):
        """Builds a Zuul source from the data that describes it.

        :param url: Address of Zuul's host.
        :type url: str
        :param cert: See :meth:`ZuulRESTClient.from_url`
        :type cert: str or None
        :key name:
            Name of the source.
            Type: str. Default: 'zuul-ci'.
        :key driver:
            Driver for this source.
            Type: str. Default: 'zuul'.
        :key priority:
            Priority of the source.
            Type: int. Default: 0.
        :key enabled:
            Whether this source is to be used.
            Type: bool. Default: True.
        :return: The instance.
        """
        kwargs.setdefault('name', 'zuul-ci')
        kwargs.setdefault('driver', 'zuul')

        return Zuul(api=ZuulRESTClient.from_url(url, cert), url=url, **kwargs)

    @speed_index({'base': 1})
    def get_tenants(self, **kwargs):
        return handle_query(self._api, **kwargs)

    @speed_index({'base': 2})
    def get_jobs(self, **kwargs):
        """Retrieves jobs present on the host.

        :param kwargs: All arguments from the command line.
            These define the query to be performed. Arguments that explicitly
            affect jobs are listed below.
        :key jobs:
            Names of the jobs to be fetched.
            Type: Argument[list[str]].
        :key job_url:
            URL of the job to be fetched.
            Type: Argument[str].
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self.get_tenants(**kwargs)

    @speed_index({'base': 3})
    def get_builds(self, **kwargs):
        """Retrieves builds present on the host.

        .. seealso::
            For filters related to jobs, see: :meth:`~.get_jobs`.

        :param kwargs: All arguments from the command line.
            These define the query to be performed. Arguments that explicitly
            affect builds are listed below.
        :key last_build:
            Fetch only the latest build of each job.
            Type: None
        :key build_id:
            List of build IDs to be fetched.
            Type: Argument[list[str]].
        :key build_status:
            List of desired statuses to be fetched.
            Type: Argument[list[str]].
        :return: Resulting CI model from the query, formatted as an
            attribute of type :class:`Tenant`.
        :rtype: :class:`AttributeDictValue`
        """
        return self.get_jobs(**kwargs)
