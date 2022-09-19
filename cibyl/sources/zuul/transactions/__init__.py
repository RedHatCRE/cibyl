"""Provides higher-level requests for the retrieval of data from Zuul. The
requests provided here abstract how the data is queried and focuses only on
its access and filtering. You may consider this module the interface between a
Zuul host and a Zuul source.

License:
#
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
#
"""
import re
from abc import ABC
from typing import Iterable

from cibyl.cli.ranged_argument import RANGE_OPERATORS, Range
from cibyl.models.ci.zuul.test import TestKind, TestStatus
from cibyl.sources.zuul.apis import ZuulBuildAPI
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest
from cibyl.sources.zuul.utils.tests.types import Test, TestResult, TestSuite
from cibyl.utils.filtering import apply_filters, matches_regex
from cibyl.utils.urls import URL


class Request(ABC):
    """Base class for any kind of request.
    """

    def __init__(self):
        """Constructor.
        """
        self._filters = []


class TenantsRequest(Request):
    """High-Level petition focused on retrieval of data related to tenants.
    """

    def __init__(self, zuul):
        """Constructor.

        :param zuul: Low-Level Zuul API.
        :type zuul: :class:`cibyl.sources.zuul.apis.ZuulAPI`
        """
        super().__init__()

        self._zuul = zuul

    def with_name(self, *pattern):
        """Will limit request to tenants whose name follows a certain pattern.

        :param pattern: Regex pattern for the desired name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`TenantsRequest`
        """

        def test(tenant):
            return any(
                matches_regex(patt, tenant.name) for patt in pattern
            )

        self._filters.append(test)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`TenantResponse`]
        """
        tenants = apply_filters(self._zuul.tenants(), *self._filters)

        return [TenantResponse(tenant) for tenant in tenants]


class ProjectsRequest(Request):
    """High-Level petition focused on retrieval of data related to projects.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Low-Level API to the tenant to get the projects from.
        :type tenant: :class:`cibyl.sources.zuul.apis.ZuulTenantAPI`
        """
        super().__init__()

        self._tenant = tenant

    def with_name(self, *pattern):
        """Will limit request to projects whose name follows a certain pattern.

        :param pattern: Regex pattern for the desired name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`ProjectRequest`
        """

        def test(project):
            return any(
                matches_regex(patt, project.name) for patt in pattern
            )

        self._filters.append(test)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`ProjectResponse`]
        """
        projects = apply_filters(self._tenant.projects(), *self._filters)

        return [ProjectResponse(project) for project in projects]


class PipelinesRequest(Request):
    """High-Level petition focused on retrieval of data related to pipelines.
    """

    def __init__(self, provider):
        """Constructor.

        :param provider: Low-Level API to the provider to get the pipelines
            from.
        :type provider: :class:`cibyl.sources.zuul.providers.PipelinesProvider`
        """
        super().__init__()

        self._provider = provider

    def with_name(self, *pattern):
        """Will limit request to pipelines whose name follows a certain
        pattern.

        :param pattern: Regex pattern for the desired name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`PipelinesRequest`
        """

        def test(pipeline):
            return any(
                matches_regex(patt, pipeline.name) for patt in pattern
            )

        self._filters.append(test)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`PipelineResponse`]
        """
        pipelines = apply_filters(self._provider.pipelines(), *self._filters)

        return [PipelineResponse(pipeline) for pipeline in pipelines]


class JobsRequest(Request):
    """High-Level petition focused on retrieval of data related to jobs.
    """

    def __init__(self, provider):
        """Constructor.

        :param provider: Low-Level API to the provider to get the jobs from.
        :type provider: :class:`cibyl.sources.zuul.providers.JobsProvider`
        """
        super().__init__()

        self._provider = provider

    def with_name(self, *pattern):
        """Will limit request to jobs whose name follows a certain pattern.

        :param pattern: Regex pattern for the desired name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`JobsRequest`
        """

        def test(job):
            return any(
                matches_regex(patt, job.name) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_url(self, *pattern):
        """Will limit request to jobs whose url follows a certain pattern.

        :param pattern: Regex pattern for the desired url.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`JobsRequest`
        """

        def test(job):
            return any(
                matches_regex(patt, job.url) for patt in pattern
            )

        self._filters.append(test)
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`JobResponse`]
        """
        jobs = apply_filters(self._provider.jobs(), *self._filters)

        return [JobResponse(job) for job in jobs]


class VariantsRequest(Request):
    """High-Level petition focused on retrieval of data related to a job's
    variants.
    """

    def __init__(self, job):
        """Constructor.

        :param job: Low-Level API to the job to get the variants from.
        :type job: :class:`cibyl.sources.zuul.apis.ZuulJobAPI`
        """
        super().__init__()

        self._job = job

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`VariantResponse`]
        """
        variants = self._job.variants()

        return [VariantResponse(variant) for variant in variants]


class BuildsRequest(Request):
    """High-Level petition focused on retrieval of data related to builds.
    """

    def __init__(self, job):
        """Constructor.

        :param job: Low-Level API to the job to get the builds from.
        :type job: :class:`cibyl.sources.zuul.apis.ZuulJobAPI`
        """
        super().__init__()

        self._job = job
        self._last_build_only = False

    def with_uuid(self, *pattern):
        """Will limit request to builds whose uuid follows a certain pattern.

        :param pattern: Regex pattern for the desired uuid.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """

        def test(build):
            return any(
                matches_regex(patt, build.uuid) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_status(self, *pattern):
        """Will limit request to builds whose status follows a certain pattern.

        :param pattern: Regex pattern for the desired status.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """

        def test(build):
            return any(
                matches_regex(patt, build.result) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_project(self, *pattern):
        """Will limit request to builds that belong to a project which
        follows a certain pattern.

        :param pattern: Regex pattern for the project's name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """

        def test(build):
            return any(
                matches_regex(patt, build.project) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_pipeline(self, *pattern):
        """Will limit request to builds that where triggered by a pipeline
        which follows a certain pattern.

        :param pattern: Regex pattern for the pipeline's name.
        :type pattern: str
        :return: The request's instance.
        :rtype: :class:`BuildsRequest`
        """

        def test(build):
            return any(
                matches_regex(patt, build.pipeline) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_last_build_only(self):
        """Will only return the latest build that meets the filters.

        :return: The request's instance.
        :rtype: :class:`BuildRequest`
        """
        # This one needs to be applied after all the other filters.
        self._last_build_only = True
        return self

    def get(self):
        """Performs the request.

        :return: Answer from the host.
        :rtype: list[:class:`BuildsResponse`]
        """
        builds = apply_filters(self._job.builds(), *self._filters)

        # Perform special filters
        if self._last_build_only:
            builds = builds[0:1]  # Just the newest build

        return [BuildResponse(build) for build in builds]


class TestsRequest(Request):
    """High-Level petition focused on retrieval of data related to test
    cases.
    """

    def __init__(self, build: ZuulBuildAPI):
        """Constructor.

        :param build: Low-Level API to the build to get the test cases from.
        """
        super().__init__()

        self._build = build

    def with_name(self, *pattern: str) -> 'TestsRequest':
        """Will limit request to tests whose name follows a certain pattern.

        :param pattern: Regex pattern for the desired test name.
        :return: The request's instance.
        """

        def test(response):
            return any(
                matches_regex(patt, response.name) for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_status(self, *pattern: str) -> 'TestsRequest':
        """Will limit request to tests on a certain status.

        :param pattern: Regex pattern for the desired test status.
        :return: The request's instance.
        """

        def test(response):
            return any(
                matches_regex(patt, response.status, flags=re.I)
                for patt in pattern
            )

        self._filters.append(test)
        return self

    def with_duration(self, *duration: Range) -> 'TestsRequest':
        """Will limit request to tests whose duration falls under the range.

        :param duration: Desired scope of the test's duration. Keep in mind
            that test duration is measured in seconds.
        :return: The request's instance.
        """

        def test(response):
            for condition in duration:
                run_test = RANGE_OPERATORS[condition.operator]

                if run_test(response.duration, condition.operand):
                    return True

            return False

        self._filters.append(test)
        return self

    def get(self) -> Iterable['TestResponse']:
        """Performs the request.

        :return: Answer from the host.
        """
        result = []

        for suite in self._build.tests():
            for test in suite.tests:
                result.append(TestResponse(self._build, suite, test))

        # Out of convenience, filters are applied to responses instead
        result = apply_filters(result, *self._filters)

        return result


class TenantResponse:
    """Response for a :class:`TenantsRequest`.
    """

    def __init__(self, tenant):
        """Constructor.

        :param tenant: Low-Level API to access the tenant's data.
        :type tenant: :class:`cibyl.sources.zuul.apis.ZuulTenantAPI`
        """
        self._tenant = tenant

    @property
    def name(self):
        """
        :return: Name of the tenant.
        :rtype: str
        """
        return self._tenant.name

    def projects(self):
        """
        :return: A request for this tenant's projects.
        :rtype: :class:`ProjectsRequest`
        """
        return ProjectsRequest(self._tenant)

    def jobs(self):
        """
        :return: A request for this tenant's jobs.
        :rtype: :class:`JobsRequest`
        """
        return JobsRequest(self._tenant)


class ProjectResponse:
    """Response for :class:`ProjectsRequest`.
    """

    def __init__(self, project):
        """Constructor.

        :param project: Low-Level API to access the project's data.
        :type project: :class:`cibyl.sources.zuul.apis.ZuulProjectAPI`
        """
        self._project = project

    @property
    def tenant(self):
        """
        :return: Response to this project's tenant.
        :rtype: :class:`TenantResponse`
        """
        return TenantResponse(self._project.tenant)

    @property
    def name(self):
        """
        :return: The project's name.
        :rtype: str
        """
        return self._project.name

    @property
    def url(self):
        """
        :return: The project's URL.
        :rtype: str
        """
        return self._project.url

    def pipelines(self):
        return PipelinesRequest(self._project)


class PipelineResponse:
    """Response for :class:`PipelinesRequest`.
    """

    def __init__(self, pipeline):
        """Constructor.

        :param pipeline: Low-Level API to access the pipeline's data.
        :type pipeline: :class:`cibyl.sources.zuul.apis.ZuulPipelineAPI`
        """
        self._pipeline = pipeline

    def __eq__(self, other):
        if not isinstance(other, PipelineResponse):
            return False

        if self is other:
            return True

        return \
            self.name == other.name and \
            self.project.name == other.project.name

    @property
    def project(self):
        """
        :return: Response to this pipeline's project.
        :rtype: :class:`ProjectResponse`
        """
        return ProjectResponse(self._pipeline.project)

    @property
    def name(self):
        """
        :return: Name of this pipeline.
        :rtype: str
        """
        return self._pipeline.name

    def jobs(self):
        """
        :return: Request for jobs belonging to this pipeline.
        :rtype: :class:`JobsRequest`
        """
        return JobsRequest(self._pipeline)


class JobResponse:
    """Response for a :class:`JobsRequest`.
    """

    def __init__(self, job):
        """Constructor.

        :param job: Low-Level API to access the job's data.
        :type job: :class:`cibyl.sources.zuul.apis.ZuulJobAPI`
        """
        self._job = job

    @property
    def tenant(self):
        """
        :return: Response to this job's tenant.
        :rtype: :class:`TenantResponse`
        """
        return TenantResponse(self._job.tenant)

    @property
    def name(self):
        """
        :return: The job's name.
        :rtype: str
        """
        return self._job.name

    @property
    def url(self):
        """
        :return: The job's URL.
        :rtype: str
        """
        return self._job.url

    def variants(self):
        """
        :return: A request to this job's variants.
        :rtype: :class:`VariantsRequest`
        """
        return VariantsRequest(self._job)

    def builds(self):
        """
        :return: A request to this job's builds.
        :rtype: :class:`BuildsRequest`
        """
        return BuildsRequest(self._job)


class VariantResponse:
    """Response for a :class:`VariantsRequest`.
    """

    def __init__(self, variant):
        """Constructor.

        :param variant: Low-Level API to access the variant's data.
        :type variant: :class:`cibyl.sources.zuul.apis.ZuulVariantAPI`
        """
        self._variant = variant

    @property
    def job(self):
        """
        :return: Response for this variant's job.
        :rtype: :class:`JobResponse`
        """
        return JobResponse(self._variant.job)

    @property
    def parent(self):
        """
        :return: Name of the parent job for this variant. 'None' if it does
            not have one.
        :rtype: str or None
        """
        return self._variant.parent

    @property
    def name(self):
        """
        :return: The variants name. Most likely, it will match its job's name.
        :rtype: str
        """
        return self._variant.name

    @property
    def description(self):
        """
        :return: Deeper information on this variant's purpose.
        :rtype: str
        """
        return self._variant.description

    @property
    def branches(self):
        """
        :return: Collection of branch names / regex patterns that indicate the
            branches the variant triggers on.
        :rtype: list[str]
        """
        result = self._variant.branches

        if not result:
            context = self._variant.context

            if context:
                result = [context.branch]

        return result

    @property
    def variables(self):
        """
        :return: Variables that specialize this variant.
        :rtype: dict[str, Any]
        """
        return self._variant.variables

    @property
    def data(self):
        """
        :return: Raw data of this variant.
        :rtype: dict[str, Any]
        """
        return self._variant.raw


class BuildResponse:
    """Response for a :class:`BuildsRequest`.
    """

    def __init__(self, build):
        """Constructor.

        :param build: Low-Level API to access the build's data.
        :type build: :class:`cibyl.sources.zuul.apis.ZuulBuildAPI`
        """
        self._build = build

    @property
    def job(self):
        """
        :return: Response for this build's job.
        :rtype: :class:`JobResponse`
        """
        return JobResponse(self._build.job)

    @property
    def data(self):
        """
        :return: Raw data of this build.
        :rtype: dict[str, Any]
        """
        return self._build.raw

    def tests(self) -> TestsRequest:
        """
        :return: A request to this build's tests.
        """
        return TestsRequest(self._build)


class TestResponse:
    """Response for a :class:`TestsRequest`.
    """

    def __init__(self, build: ZuulBuildAPI, suite: TestSuite, test: Test):
        """Constructor.

        :param build: Low-Level API to access the build's data.
        :param suite: The test suite the test belongs to.
        :param test: Data on the test case.
        """
        self._build = build
        self._suite = suite
        self._test = test

    @property
    def build(self) -> BuildResponse:
        """
        :return: Response for the test's build.
        """
        return BuildResponse(self._build)

    @property
    def suite(self) -> TestSuite:
        """
        :return: Suite the test belongs to.
        """
        return self._suite

    @property
    def kind(self) -> TestKind:
        """
        :return: Type of the test case.
        """
        if isinstance(self.data, TempestTest):
            return TestKind.TEMPEST

        return TestKind.UNKNOWN

    @property
    def name(self) -> str:
        """
        :return: Name of the test case.
        """
        return self.data.name

    @property
    def status(self) -> TestStatus:
        """
        :return: Result of the test case.
        """
        result = self.data.result

        if result == TestResult.SUCCESS:
            return TestStatus.SUCCESS

        if result == TestResult.FAILURE:
            return TestStatus.FAILURE

        if result == TestResult.SKIPPED:
            return TestStatus.SKIPPED

        return TestStatus.UNKNOWN

    @property
    def duration(self) -> float:
        """
        :return: How long the test case took to complete, in seconds.
        """
        return self.data.duration

    @property
    def url(self) -> URL:
        """
        :return: URL to the source of the test case data.
        """
        return URL(self.data.url)

    @property
    def data(self) -> Test:
        """
        :return: Raw data of this test.
        """
        return self._test
