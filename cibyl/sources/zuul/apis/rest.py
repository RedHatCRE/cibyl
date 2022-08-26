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
from typing import Iterable, NamedTuple

from overrides import overrides
from requests import Session

from cibyl.sources.zuul.apis import (ZuulAPI, ZuulBuildAPI, ZuulJobAPI,
                                     ZuulPipelineAPI, ZuulProjectAPI,
                                     ZuulTenantAPI, ZuulVariantAPI)
from cibyl.sources.zuul.apis.http import ZuulHTTPBuildAPI, ZuulSession
from cibyl.sources.zuul.utils.tests.finder import TestFinder
from cibyl.sources.zuul.utils.tests.tempest.finder import TempestTestFinder
from cibyl.sources.zuul.utils.tests.types import TestSuite

LOG = logging.getLogger(__name__)


class ZuulBuildRESTClient(ZuulHTTPBuildAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    class Tools(NamedTuple):
        """Extra tools this uses to do its job.
        """
        finders: Iterable[TestFinder] = (TempestTestFinder(),)
        """Collection of tools used to get the build's tests from all
        possible sources."""

    def __init__(self, session, job, build, tools=Tools()):
        """Constructor. See parent for more information.

        :param tools: Extra tools this uses to do its job.
        :type tools: :class:`ZuulBuildRESTClient.Tools`
        """
        super().__init__(session, job, build)

        self._tools = tools

    def __eq__(self, other):
        if not issubclass(type(other), ZuulBuildAPI):
            return False

        if self is other:
            return True

        return \
            self.job == other.job and \
            self.raw == other.raw

    @property
    def tools(self):
        return self._tools

    @overrides
    def tests(self) -> Iterable[TestSuite]:
        result = []

        for finder in self.tools.finders:
            result += finder.find(self)

        return result

    @overrides
    def close(self):
        self._session.close()


class ZuulVariantRESTClient(ZuulVariantAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session, job, variant):
        """Constructor. See parent for more information.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(job, variant)

        self._session = session

    def __eq__(self, other):
        if not issubclass(type(other), ZuulVariantAPI):
            return False

        if self is other:
            return True

        return \
            self.job == other.job and \
            self.raw == other.raw

    def close(self):
        self._session.close()


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
    def session(self):
        return self._session

    @property
    def url(self):
        base = self._session.host[:-1]
        tenant = self.tenant

        return f"{base}/t/{tenant.name}/job/{self.name}"

    @overrides
    def variants(self):
        url = f'tenant/{self.tenant.name}/job/{self.name}'
        variants = self._session.get(url)

        return [
            ZuulVariantRESTClient(self._session, self, variant)
            for variant in variants
        ]

    @overrides
    def builds(self):
        url = f'tenant/{self.tenant.name}/builds?job_name={self.name}'
        builds = self._session.get(url)

        return [
            ZuulBuildRESTClient(self._session, self, build)
            for build in builds
        ]

    @overrides
    def close(self):
        self._session.close()


class ZuulPipelineRESTClient(ZuulPipelineAPI):
    """Implementation of a Zuul client through the use of Zuul's REST-API.
    """

    def __init__(self, session, project, pipeline):
        """Constructor. See parent class for more information.

        :param session: The link through which the REST-API will be contacted.
        :type session: :class:`ZuulSession`
        """
        super().__init__(project, pipeline)

        self._session = session

    def __eq__(self, other):
        if not issubclass(type(other), ZuulPipelineAPI):
            return False

        if self is other:
            return True

        return self.project == other.project and self.name == other.name

    @property
    def session(self):
        return self._session

    @overrides
    def jobs(self):
        result = []

        for job in self._pipeline['jobs']:
            for variant in job:
                result.append(
                    ZuulJobRESTClient(
                        self._session, self._project.tenant, variant
                    )
                )

        return result

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
    def session(self):
        return self._session

    @property
    def url(self):
        base = self._session.host[:-1]
        tenant = self.tenant

        return f"{base}/t/{tenant.name}/project/{self.name}"

    @overrides
    def pipelines(self):
        result = []

        project = self._session.get(
            f"tenant/{self.tenant.name}/project/{self._project['name']}"
        )

        # Pipelines are stored under the 'configs' section of the project
        for config in project['configs']:
            # Each config has its own share of pipelines
            for pipeline in config['pipelines']:
                result.append(
                    ZuulPipelineRESTClient(
                        self._session, self, pipeline
                    )
                )

        return result

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

    @property
    def session(self):
        return self._session

    @overrides
    def projects(self):
        result = []

        for project in self._session.get(f'tenant/{self.name}/projects'):
            result.append(ZuulProjectRESTClient(self._session, self, project))

        return result

    @overrides
    def jobs(self):
        result = []

        for job in self._session.get(f'tenant/{self.name}/jobs'):
            result.append(ZuulJobRESTClient(self._session, self, job))

        return result

    @overrides
    def builds(self):
        return self._session.get(f'tenant/{self.name}/builds')

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

    @property
    def session(self):
        return self._session

    @overrides
    def info(self):
        return self._session.get('info')

    @overrides
    def tenants(self):
        result = []

        for tenant in self._session.get('tenants'):
            result.append(ZuulTenantRESTClient(self._session, tenant))

        return result

    @overrides
    def close(self):
        self._session.close()
