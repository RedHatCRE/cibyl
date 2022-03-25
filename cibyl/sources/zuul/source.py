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
from itertools import chain
from typing import Iterable

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source
from cibyl.sources.zuul.apis.rest import ZuulRESTClient
from cibyl.utils.filtering import apply_filters


class Zuul(Source):
    """Source implementation for a Zuul host.
    """

    class API:
        def __init__(self, parent, api):
            self._parent = parent
            self._api = api

        def get_jobs(self, **kwargs):
            def retrieve_jobs():
                def is_job_a_target(job):
                    # Check if user wants to filter jobs
                    if 'jobs' not in kwargs:
                        return True

                    targets = kwargs.get('jobs').value

                    if not isinstance(targets, Iterable):
                        return True

                    # Check if this job is desired by user
                    if job.name in targets:
                        return True

                    return False

                return apply_filters(
                    chain.from_iterable(
                        tenant.jobs() for tenant in self._api.tenants()
                    ),
                    lambda job: is_job_a_target(job)
                )

            def build_job_model(job):
                def make_job_url():
                    """Builds the URL where the job can be found at. Do not
                    confuse this URL with the job's REST end-point.

                    :return: The address where the job can be found at.
                    :rtype: str
                    """
                    base = self._parent.url
                    tenant = job.tenant

                    return f"{base}/t/{tenant.name}/job/{job.name}"

                builds = None

                if 'builds_at' in kwargs:
                    builds = kwargs['builds_at'](job)

                return Job(name=job.name, url=make_job_url(), builds=builds)

            return AttributeDictValue(
                name='jobs',
                attr_type=Job,
                value={
                    job.name: build_job_model(job)
                    for job in retrieve_jobs()
                }
            )

        def get_builds(self, **kwargs):
            def retrieve_builds(job):
                def last_build_filter(build):
                    if 'last_build' not in kwargs:
                        return True

                    return build == builds[0]

                builds = job.builds()
                builds = apply_filters(builds, last_build_filter)

                return {
                    build['uuid']: Build(build['uuid'], build['result'])
                    for build in builds
                }

            return self.get_jobs(builds_at=retrieve_builds, **kwargs)

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

        self._api = Zuul.API(self, api)

    @staticmethod
    def new_source(url, cert=None, **kwargs):
        """Builds a Zuul source from the data that describes it.

        :param url: Address of Zuul's host.
        :type url: str
        :param cert: See :meth:`ZuulRESTClient.from_url`
        :type cert: str or None
        :key name: Name of the source. Type: str. Default: 'zuul-ci'.
        :key driver: Driver for this source. Type: str. Default: 'zuul'.
        :key priority: Priority of the source. Type: int. Default: 0.
        :key enabled: Whether this source is to be used.
            Type: bool. Default: True.
        :return: The instance.
        """
        kwargs.setdefault('name', 'zuul-ci')
        kwargs.setdefault('driver', 'zuul')

        return Zuul(api=ZuulRESTClient.from_url(url, cert), url=url, **kwargs)

    def get_jobs(self, **kwargs):
        """Retrieves jobs present on the host.

        :return: The jobs retrieved from the query, formatted as an attribute
            of type :class:`Job`. Jobs are indexed by their name on the
            attribute.
        :rtype: :class:`AttributeDictValue`
        """
        return self._api.get_jobs(**kwargs)

    def get_builds(self, **kwargs):
        """Retrieves builds present on the host.

        :param kwargs: Parameters which narrow down the builds to search for.
            Currently, the accepted parameters are:
                * jobs -> list[str]: Name of jobs to search for.
        :type kwargs: :class:`cibyl.cli.argument.Argument`
        :return: The jobs retrieved from the query, formatted as an attribute
            of type :class:`Job`. Jobs are indexed by their name on the
            attribute. Builds can be found inside each of the jobs listed here.
        :rtype: :class:`AttributeDictValue`
        """
        return self._api.get_builds(**kwargs)
