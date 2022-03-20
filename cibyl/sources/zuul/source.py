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


class ZuulData:
    """Data class representing the source side of Zuul.
    """

    def __init__(self, name='zuul-ci', driver='zuul', priority=0):
        """Constructor.

        :param name: Name of the source.
        :type name: str
        :param driver: Name of the driver used by the source.
        :type driver: str
        :param priority: The source's priority.
        :type priority: int
        """
        self.name = name
        self.driver = driver
        self.priority = priority


class Zuul(Source):
    """Source implementation for a Zuul host.
    """

    def __init__(self, api, url, data=ZuulData()):
        """Constructor.

        :param api: Medium of communication with host.
        :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
        :param url: Address where the host is located.
        :type url: str
        :param data: Additional information detailing the source.
        :type data: :class:`ZuulData`
        """
        # URLs are built assuming no slash at the end of URL
        if url.endswith('/'):
            url = url[:-1]  # Removes last character of string

        super().__init__(data.name, data.driver, url, data.priority)

        self._api = api

    @staticmethod
    def new_source(url, cert=None, data=ZuulData()):
        """Builds a Zuul source from the data that describes it.

        :param url: Address of Zuul's host.
        :type url: str
        :param cert: See :meth:`ZuulRESTClient.from_url`
        :type cert: str or None
        :param data: Additional data describing the source.
        :type data: :class:`ZuulData`
        :return: The instance.
        """
        return Zuul(ZuulRESTClient.from_url(url, cert), url, data)

    def connect(self):
        self._api.info()

    def query(self, system, args):
        raise NotImplementedError

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

        def is_job_a_target(job):
            """
            :param job: Name of the job to check.
            :type job: str
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
            if job in targets:
                return True

            return False

        def build_job_url(tenant, job):
            """Builds the URL where the job can be found at. Do not confuse
            this URL with the job's REST end-point.

            :param tenant: Tenant to which the job belongs to.
            :type tenant: :class:`ZuulTenantAPI`
            :param job: The JSON obtained from the remote which represents
                the job.
            :type job: dict
            :return: The address where the job can be found at.
            :rtype: str
            """
            return f"{self.url}/t/{tenant.name}/job/{job['name']}"

        def get_jobs_in_zuul():
            """Performs the query, retrieving all jobs as described
            by the delimiting inputs.

            :return: The jobs, indexed by their name.
            :rtype: dict[str, :class:`Job`]
            """
            zuul_jobs = {}

            for tenant in self._api.tenants():
                for job in tenant.jobs():
                    name = job['name']

                    if is_job_a_target(name):
                        zuul_jobs[name] = Job(name, build_job_url(tenant, job))

            return zuul_jobs

        return AttributeDictValue(
            'jobs',
            attr_type=Job,
            value=get_jobs_in_zuul()
        )

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
        result = self.get_jobs(**kwargs)

        jobs = result.value

        for tenant in self._api.tenants():
            for build in tenant.builds():
                # The job the build belongs to
                build_job = build['job_name']

                # Check if build is desired
                if build_job not in jobs.keys():
                    continue

                # Add build to job
                job = jobs.get(build_job)
                job.add_build(Build(build['uuid'], build['result']))

        return result
