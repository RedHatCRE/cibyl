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
from typing import Iterable

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source
from cibyl.sources.zuul.apis.rest import ZuulRESTClient


class Zuul(Source):
    """Source implementation for a Zuul host.
    """

    class Jobs:
        """Extends actions that the source can do with regard to jobs.
        """

        def __init__(self, parent):
            """Constructor.

            :param parent: Source this extends.
            :type parent: :class:`Zuul`
            """
            self._parent = parent

        @property
        def api(self):
            """
            :return: Link this uses to perform queries with.
            :rtype: :class:`cibyl.sources.zuul.api.ZuulAPI`
            """
            return self._parent.api

        @staticmethod
        def is_job_a_target(job, **kwargs):
            """
            :return: Whether the query is asking for this job or not.
            :rtype: bool
            """
            # Check if user wants to filter jobs
            if 'jobs' not in kwargs:
                return True

            targets = kwargs.get('jobs').value

            if not targets:
                return True

            if not isinstance(targets, Iterable):
                return True

            # Check if this job is desired by user
            if job.name in targets:
                return True

            return False

        def build_job_url(self, tenant, job):
            """Builds the URL where the job can be found at. Do not confuse
            this URL with the job's REST end-point.

            :return: The address where the job can be found at.
            :rtype: str
            """
            return f"{self._parent.url}/t/{tenant.name}/job/{job.name}"

        def get_jobs_in_zuul(self, **kwargs):
            """Provides a link to the jobs present on the host that meet
            the filters described on the keyed arguments.

            :key jobs: Name of the desired jobs. Type: list[str].
                Default: None.
            :return: The jobs.
            :rtype: list[:class:`sources.zuul.api.ZuulJobAPI`]
            """
            result = []

            for tenant in self.api.tenants():
                for job in tenant.jobs():
                    if self.is_job_a_target(job, **kwargs):
                        result.append(job)

            return result

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
        self._jobs = Zuul.Jobs(self)

    @property
    def api(self):
        """
        :return: Link this uses to perform queries with.
        :rtype: :class:`cibyl.sources.zuul.api.ZuulAPI`
        """
        return self._api

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

        :param kwargs: Parameters which narrow down the jobs to search for.
            Currently, the accepted parameters are:
                * jobs -> list[str]: Name of jobs to search for.
        :type kwargs: :class:`cibyl.cli.argument.Argument`
        :return: The jobs retrieved from the query, formatted as an attribute
            of type :class:`Job`. Jobs are indexed by their name on the
            attribute.
        :rtype: :class:`AttributeDictValue`
        """
        jobs = {}

        for job in self._jobs.get_jobs_in_zuul(**kwargs):
            name = job.name
            tenant = job.tenant

            jobs[name] = Job(
                name,
                self._jobs.build_job_url(tenant, job)
            )

        return AttributeDictValue('jobs', attr_type=Job, value=jobs)

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
        jobs = {}

        for job in self._jobs.get_jobs_in_zuul(**kwargs):
            name = job.name
            tenant = job.tenant

            builds = {}

            for build in job.builds():
                uuid = build['uuid']

                builds[uuid] = Build(build['uuid'], build['result'])

            jobs[name] = Job(
                name,
                self._jobs.build_job_url(tenant, job),
                builds
            )

        return AttributeDictValue('jobs', attr_type=Job, value=jobs)
