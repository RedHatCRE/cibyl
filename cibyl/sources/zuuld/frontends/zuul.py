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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generic, Iterable, Optional

from overrides import overrides

from cibyl.sources.zuul.apis import (ZuulAPI, ZuulJobAPI, ZuulTenantAPI,
                                     ZuulVariantAPI)
from cibyl.sources.zuul.apis.factories.abc import ZuulAPIFactory
from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.backends.git import GitBackend
from cibyl.sources.zuuld.errors import InvalidURL, UnsupportedError
from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.specs.git import GitSpec
from kernel.tools.cache import Cache, RTCache
from kernel.tools.json import NullValidatorFactory
from kernel.tools.urls import URL

LOG = logging.getLogger(__name__)


@dataclass
class Session(Generic[T]):
    """Defines the repositories the frontend works with, as well as the
    backend used to interact with them.

    The type of spec and the backend that supports them must match,
    as indicated by the generic type.
    """
    specs: Iterable[T]
    """Defines the location of all Zuul.D data available to the source."""
    backend: ZuulDBackend[T]
    """API that allows interaction with the specs."""


class _Variant(Generic[T], ZuulVariantAPI):
    """Side of the frontend meant for variant operations.
    """

    def __init__(self, job: '_Job', data: Dict):
        """Constructor.

        :param job: Job this variant belongs to.
        :param data: Raw data describing the variant this represents.
        """
        super().__init__(job, data)

        self._owner = job

    @property
    def owner(self) -> '_Job':
        """
        :return:
            Job this variant belongs to, cast to Zuul.D's representation of so.
        """
        return self._owner

    @overrides
    def close(self):
        return


class _Job(Generic[T], ZuulJobAPI):
    """Side of the frontend meant for job operations.
    """

    def __init__(
        self,
        session: Session[T],
        spec: T,
        tenant: '_Tenant',
        data: Dict
    ):
        """Constructor.

        :param session: Description of what the interface interacts with.
        :param spec: Spec this job originated from.
        :param tenant: Tenant this job is under.
        :param data: Raw data describing the job this represents.
        """
        super().__init__(tenant, data)

        self._session = session
        self._spec = spec
        self._owner = tenant

    @property
    def session(self) -> Session[T]:
        """
        :return: Description of what the interface interacts with.
        """
        return self._session

    @property
    def spec(self) -> T:
        """
        :return: Spec this job originated from.
        """
        return self._spec

    @property
    def owner(self) -> '_Tenant':
        return self._owner

    @property
    @overrides
    def url(self):
        return self.spec.remote

    @overrides
    def variants(self):
        result = []

        for job in self.owner.cache.get(self.spec):
            if job.name != self.name:
                continue

            result.append(
                _Variant(
                    job=self,
                    data={
                        'name': job.name,
                        'parent': job.parent,
                        'description': '',
                        'branches': job.branches,
                        'variables': job.vars,
                        'source_context': None
                    }
                )
            )

        return result

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class _Tenant(Generic[T], ZuulTenantAPI):
    """Side of the frontend meant for tenant operations.
    """

    def __init__(
        self,
        session: Session[T],
        data: Dict,
        cache: Optional[Cache[T, Iterable[Job]]] = None
    ):
        """Constructor.

        :param session: Description of what the interface interacts with.
        :param data: Raw data describing the tenant this represents.
        """
        if cache is None:
            cache = RTCache(
                loader=lambda spec: self.session.backend.get.jobs(spec)
            )

        super().__init__(data)

        self._session = session
        self._cache = cache

    @property
    def session(self) -> Session[T]:
        """
        :return: Description of what the interface interacts with.
        """
        return self._session

    @property
    def cache(self) -> Cache[T, Iterable[Job]]:
        return self._cache

    @overrides
    def projects(self):
        raise UnsupportedError

    @overrides
    def jobs(self):
        result = []

        for spec in self.session.specs:
            for job in self.cache.get(spec):
                result.append(
                    _Job(
                        session=self.session,
                        spec=spec,
                        tenant=self,
                        data={
                            'name': job.name
                        }
                    )
                )

        return result

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class ZuulFrontend(Generic[T], ZuulAPI):
    """Implementation of a Zuul client through the use of a Zuul.D backend.

    This acts as an interface between the Zuul source and the Zuul.D
    implementation so that it can be used as a provider of data to the
    source, much like the REST-API already does.

    Depending on the origin of the Zuul.D data, this interface will connect
    to different kinds of backends as defined by the generic type.
    """

    def __init__(self, session: Session[T]):
        """Constructor.

        :param session: Description of what the interface interacts with.
        """
        self._session = session

    @property
    def session(self) -> Session[T]:
        """
        :return: Description of what the interface interacts with.
        """
        return self._session

    @overrides
    def info(self):
        raise UnsupportedError

    @overrides
    def tenants(self):
        return [
            _Tenant(
                session=self.session,
                data={
                    'name': 'zuul.d'
                }
            )
        ]

    @overrides
    def close(self):
        return


class GitFrontendFactory(ZuulAPIFactory):
    """Factory for :class:`ZuulFrontend` specialized for handling Git specs.
    """

    def __init__(
        self,
        specs: Iterable[GitSpec],
        backend: ZuulDBackend[GitSpec]
    ):
        """Constructor.

        :param specs: Specs to create the session for.
        :param backend: Backend to support the specs with.
        """
        self._specs = specs
        self._backend = backend

    @staticmethod
    def from_kwargs(**kwargs) -> 'GitFrontendFactory':
        """Builds a new instance of the factory from a collection of
        unknown arguments.

        :param kwargs: Keyword arguments.
        :key repos: Required. Repositories that hold the Zuul.D data.
        :return: A new instance of the factory.
        :raise ValueError:
            If keyword arguments are missing 'repos' key.
        """
        if 'repos' not in kwargs:
            raise ValueError(
                "Missing key: 'repos' from keyword arguments."
            )

        return GitFrontendFactory(
            specs=GitFrontendFactory._get_specs_from(**kwargs),
            backend=GitFrontendFactory._get_backend_from(**kwargs)
        )

    @staticmethod
    def _get_specs_from(**kwargs) -> Iterable[GitSpec]:
        result = []

        for repo in kwargs['repos']:
            url = repo['url']
            path = 'zuul.d/'

            try:
                result.append(
                    GitSpec(
                        remote=URL(url),
                        directory=Path(path)
                    )
                )
            except InvalidURL:
                LOG.debug(
                    "Ignoring url: '%s' during git backend creation as it "
                    "is not a valid git url.",
                    url
                )
                continue

        return result

    @staticmethod
    def _get_backend_from(**kwargs) -> ZuulDBackend[GitSpec]:
        backend = GitBackend()

        if kwargs.get('unsafe', False):
            LOG.info(
                "Unsafe mode turned on! "
                "Disabling YAML validation on Git backend..."
            )

            # Inject 'bypass' validator on Zuul.D file interpreters
            get = backend.get
            yamls = get.tools.files
            zuulds = yamls.tools.files
            zuulds.tools.validators = NullValidatorFactory()

        return backend

    @property
    def specs(self) -> Iterable[GitSpec]:
        """
        :return: Specs to create a session for.
        """
        return self._specs

    @property
    def backend(self) -> ZuulDBackend[GitSpec]:
        """
        :return: Backend that supports the session.
        """
        return self._backend

    @overrides
    def new(self) -> ZuulFrontend[GitSpec]:
        return ZuulFrontend(
            session=Session(
                specs=self.specs,
                backend=self.backend
            )
        )
