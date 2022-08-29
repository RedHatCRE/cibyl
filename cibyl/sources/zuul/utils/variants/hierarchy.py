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
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence

from cibyl.sources.zuul.transactions import JobResponse as Job
from cibyl.sources.zuul.transactions import TenantResponse as Tenant
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from cibyl.utils.filtering import matches_regex

Variables = Dict[str, Any]


class SearchError(Exception):
    pass


class JobFinder:
    class Search:
        def __init__(self, job: str):
            self._job = job

        def within(self, tenant: Tenant) -> Job:
            request = tenant.jobs()
            request.with_name(f'^{self._job}$')

            result = request.get()

            if len(result) == 0:
                raise SearchError(
                    f"No job with name: '{self._job}' "
                    f"found in tenant: '{tenant.name}'."
                )

            if len(result) > 1:
                raise SearchError(
                    f"More than one job with name: '{self._job} "
                    f"found in tenant: '{tenant.name}'."
                )

            return result[0]

        @property
        def job(self) -> str:
            return self._job

    def find(self, job: str) -> Search:
        return JobFinder.Search(job)


class VariantFinder:
    class Search:
        def __init__(self, tools: 'VariantFinder.Tools'):
            self._tools = tools

        def parent_of(self, variant: Variant) -> Optional[Variant]:
            parent = variant.parent

            if not parent:
                return None

            job = self.tools.jobs.find(parent).within(variant.job.tenant)

            for candidate in job.variants().get():
                for condition in candidate.branches:
                    for branch in variant.branches:
                        if matches_regex(condition, branch):
                            return candidate

            raise SearchError(
                f"Could not find parent variant for: '{variant.name}'."
            )

        @property
        def tools(self) -> 'VariantFinder.Tools':
            return self._tools

    @dataclass
    class Tools:
        jobs: JobFinder = field(
            default_factory=lambda: JobFinder()
        )

    def __init__(self, tools: Optional[Tools] = None):
        if tools is None:
            tools = VariantFinder.Tools()

        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def find(self) -> Search:
        return VariantFinder.Search(
            tools=self.tools
        )


class HierarchyCrawler:
    class Iterator:
        def __init__(self, start: Variant, tools: 'HierarchyCrawler.Tools'):
            self._step = None
            self._start = start
            self._tools = tools

        def __next__(self) -> Variant:
            next_step = self._get_next_step()

            if not next_step:
                raise StopIteration

            self._step = next_step
            return self._step

        def _get_next_step(self) -> Variant:
            if self._step is None:
                return self._start

            return self.tools.variants.find().parent_of(self._step)

        @property
        def start(self) -> Variant:
            return self._start

        @property
        def tools(self) -> 'HierarchyCrawler.Tools':
            return self._tools

    @dataclass
    class Tools:
        variants: VariantFinder = field(
            default_factory=lambda: VariantFinder()
        )

    def __init__(self, variant: Variant, tools: Optional[Tools] = None):
        if tools is None:
            tools = HierarchyCrawler.Tools()

        self._variant = variant
        self._tools = tools

    def __iter__(self) -> Iterator:
        return HierarchyCrawler.Iterator(
            start=self.variant,
            tools=self.tools
        )

    @property
    def variant(self):
        return self._variant

    @property
    def tools(self):
        return self._tools


class HierarchyCrawlerFactory:
    def from_variant(self, variant: Variant) -> HierarchyCrawler:
        return HierarchyCrawler(variant)


class HierarchyBuilder:
    class VariantTask:
        def __init__(self, variant: Variant, tools: 'HierarchyBuilder.Tools'):
            self._variant = variant
            self._tools = tools

        def build(self) -> Sequence[Variant]:
            crawler = self.tools.crawlers.from_variant(self.variant)

            return [*crawler]

        @property
        def variant(self) -> Variant:
            return self._variant

        @property
        def tools(self) -> 'HierarchyBuilder.Tools':
            return self._tools

    @dataclass
    class Tools:
        crawlers: HierarchyCrawlerFactory = field(
            default_factory=lambda: HierarchyCrawlerFactory()
        )

    def __init__(self, tools: Optional[Tools] = None):
        if tools is None:
            tools = HierarchyBuilder.Tools()

        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def from_variant(self, variant: Variant) -> VariantTask:
        return HierarchyBuilder.VariantTask(
            variant=variant,
            tools=self.tools
        )


class RecursiveVariableSearch:
    @dataclass
    class Tools:
        hierarchy: HierarchyBuilder = field(
            default_factory=lambda: HierarchyBuilder()
        )

    def __init__(self, variant: Variant, tools: Optional[Tools] = None):
        if tools is None:
            tools = RecursiveVariableSearch.Tools()

        self._variant = variant
        self._tools = tools

    @property
    def variant(self):
        return self._variant

    @property
    def tools(self):
        return self._tools

    def search(self) -> Variables:
        result = {}

        hierarchy = self.tools.hierarchy.from_variant(self.variant).build()
        hierarchy = reversed(hierarchy)

        for level in hierarchy:
            result.update(level.variables)

        return result


class RecursiveVariableSearchFactory:
    def from_variant(self, variant: Variant) -> RecursiveVariableSearch:
        return RecursiveVariableSearch(variant)
