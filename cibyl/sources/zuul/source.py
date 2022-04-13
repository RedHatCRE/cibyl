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

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.source import Source, speed_index
from cibyl.sources.zuul.apis.rest import ZuulRESTClient
from cibyl.utils.filtering import apply_filters


class Zuul(Source):
    """Source implementation for a Zuul host.
    """

    class API:
        """The meat of the source. Provides its capabilities without being
        restricted by the interface definition.
        """

        def __init__(self, parent, api):
            """Constructor.

            :param parent: The source this gives capabilities to.
            :type parent: :class:`Zuul`
            :param api: Low-Level Zuul client.
            :type api: :class:`cibyl.sources.zuul.api.ZuulAPI`
            """
            self._parent = parent
            self._api = api

        def get_jobs(self, fetch_builds=False, **kwargs):
            """Gets a set of jobs from the host formatted with the job model.

            :param fetch_builds: Whether to also download the jobs builds.
            :type fetch_builds: bool
            :key jobs: List of jobs to be fetched. Type: Argument[list[str]].
                Default: None.
            :key last_build: Fetch only the latest build of each job. Does
                nothing if build fetching is not requested. Type: bool.
                Default: False.
            :return: The jobs in the format of an attribute.
            :rtype: :class:`AttributeDictValue`
            """

            def get_model_for(job):
                model = Job(
                    name=job.name,
                    url=self._get_url_for(job)
                )

                if fetch_builds:
                    for build in self._get_builds_for(job, **kwargs):
                        model.add_build(Build(build['uuid'], build['result']))

                return model

            def get_targets():
                if 'jobs' not in kwargs:
                    return []

                return kwargs['jobs'].value

            jobs = apply_filters(
                chain.from_iterable(
                    tenant.jobs() for tenant in self._api.tenants()
                ),
                lambda job: self._is_job_a_target(get_targets(), job)
            )

            return AttributeDictValue(
                name='jobs',
                attr_type=Job,
                value={
                    job.name: get_model_for(job)
                    for job in jobs
                }
            )

        @staticmethod
        def _get_builds_for(job, **kwargs):
            """Gets the builds of a job formatted as raw data.

            :param job: The job to get the build for.
            :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
            :key last_build: Fetch only the latest build of each job. Does
                nothing if build fetching is not requested. Type: bool.
                Default: False.
            :return: Information about the job's builds.
            :rtype: list[dict]
            """

            def last_build_filter(build):
                if 'last_build' not in kwargs:
                    return True

                return build == builds[0]

            def build_status_filter(build):
                if 'build_status' not in kwargs:
                    return True

                return build['result'] in kwargs['build_status'].value

            builds = job.builds()

            return apply_filters(
                builds,
                last_build_filter,
                build_status_filter
            )

        @staticmethod
        def _is_job_a_target(targets, job):
            """Implements the '--jobs job1 job2 ...' filter.

            :param targets: Name of the jobs that are considered targets.
                All jobs will be considered a target if this is empty.
            :type targets: list[str]
            :param job: The job to check.
            :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
            :return: Whether it is or not.
            :rtype: bool
            """
            if not targets:
                return True

            return job.name in targets

        def _get_url_for(self, job):
            """Builds the URL where the job is located at. This URL is meant
            to be seen on a browser, do not confuse it with the API
            counterpart.

            :param job: The job to build the URL for.
            :type job: :class:`cibyl.sources.zuul.api.ZuulJobAPI`
            :return: The URL.
            :rtype: str
            """
            base = self._parent.url
            tenant = job.tenant

            return f"{base}/t/{tenant.name}/job/{job.name}"

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

    @speed_index({'base': 3})
    def get_jobs(self, **kwargs):
        """Retrieves jobs present on the host.

        :return: The jobs retrieved from the query, formatted as an attribute
            of type :class:`Job`. Jobs are indexed by their name on the
            attribute.
        :rtype: :class:`AttributeDictValue`
        """
        return self._api.get_jobs(fetch_builds=False, **kwargs)

    @speed_index({'base': 3})
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
        return self._api.get_jobs(fetch_builds=True, **kwargs)
