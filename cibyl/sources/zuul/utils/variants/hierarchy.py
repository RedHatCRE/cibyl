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
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence

from cibyl.exceptions.source import SourceException
from cibyl.sources.zuul.transactions import JobResponse as Job
from cibyl.sources.zuul.transactions import TenantResponse as Tenant
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from cibyl.utils.filtering import matches_regex

LOG = logging.getLogger(__name__)

Variables = Dict[str, Any]
"""Type for a variant's variables."""


class SearchError(SourceException):
    """Represents any error occurring during a search on the Zuul host.
    """


class JobFinder:
    """Allows for easy search of a job along the Zuul host.
    """

    class Search:
        """Action waiting for conditions to given to perform the search.
        """

        def __init__(self, job: str):
            """Constructor.

            :param job: Name of the job to look for.
            """
            self._job = job

        def within(self, tenant: Tenant) -> Job:
            """Searches for the job throughout the given tenant.

            :param tenant: The tenant to look through.
            :return: The found job.
            :raises SearchError:
                If the job is not in the tenant.
                If the job name leads to more than one job, which should
                never happen.
            """
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
            """
            :return: Name of the job this targets.
            """
            return self._job

    def find(self, job: str) -> Search:
        """Open up a new search action for the given job.

        :param job: Name of the job to search.
        :return: Instance to a searcher.
        """
        return JobFinder.Search(job)


class VariantFinder:
    """Allows for easy search of a variant along the Zuul host.
    """

    class Search:
        """Action waiting for conditions to given to perform the search.
        """

        def __init__(self, tools: 'VariantFinder.Tools'):
            """Constructor.

            :param tools: Tools this uses to do its job.
            """
            self._tools = tools

        def parent_of(self, variant: Variant) -> Optional[Variant]:
            """Searches of the parent variant of the given one.

            A parent variant is the first one that:
                - Belongs to the parent job of the variant.
                - Spans any of the branches from the variant.

            :param variant: The variant to get the parent for.
            :return: The parent variant.
            :raises SearchError:
                If the parent job could not be found.
                If the parent variant could not be found.
            """
            parent = variant.parent

            if not parent:
                return None

            job = self.tools.jobs.find(parent).within(variant.job.tenant)

            for candidate in job.variants().get():
                for condition in candidate.branches:
                    for branch in variant.branches:
                        # See if parent pattern matches my branch
                        if matches_regex(condition, branch):
                            return candidate

                        # See if my pattern matches my parent's branch
                        if matches_regex(branch, condition):
                            return candidate

            raise SearchError(
                f"Could not find parent variant for: '{variant.name}'."
            )

        @property
        def tools(self) -> 'VariantFinder.Tools':
            """
            :return: Tools this uses to do its job.
            """
            return self._tools

    @dataclass
    class Tools:
        """Tools this uses to do its job.
        """
        jobs: JobFinder = field(
            default_factory=lambda: JobFinder()
        )
        """Used to search for the parent job of a variant."""

    def __init__(self, tools: Optional[Tools] = None):
        """Constructor.

        :param tools: Tools this uses to do its job.
        """
        if tools is None:
            tools = VariantFinder.Tools()

        self._tools = tools

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its job.
        """
        return self._tools

    def find(self) -> Search:
        """Opens up a new search action.

        :return: The action instance.
        """
        return VariantFinder.Search(
            tools=self.tools
        )


class HierarchyCrawler:
    """Iterates over all parents leading up to a variant. Iteration order
    goes from a variant up to its base job, including the starting variant
    itself. It can be reused as each iteration restarts from the starting
    variant.
    """

    class Iterator:
        """Will iterate from a particular variant, parent by parent,
        up to the base job, at which point it will stop.

        Implements '__next__' in order for it to be used on for loops.
        """

        def __init__(self, start: Variant, tools: 'HierarchyCrawler.Tools'):
            """Constructor.

            :param start: Variant this will begin iterating from. The
                iterator is inclusive, meaning that this variant will be
                part of the sequence, the first step.
            :param tools: Tools this uses to do its task.
            """
            self._step = None
            self._start = start
            self._tools = tools

        def __next__(self) -> Variant:
            next_step = self._get_next_step()

            # Have we reached the base job?
            if not next_step:
                raise StopIteration

            self._step = next_step
            return self._step

        def _get_next_step(self) -> Optional[Variant]:
            # Make the start variant be part of the iteration
            if self._step is None:
                return self._start

            try:
                return self.tools.variants.find().parent_of(self._step)
            except SearchError as ex:
                LOG.warning(
                    "Prematurely finished iterating over hierarchy for: '%s'. "
                    "Reason: '%s'. "
                    "Results may be incomplete as a consequence.",
                    self._start.name, ex
                )
                return None

        @property
        def start(self) -> Variant:
            """
            :return: Variant this begins iterating from.
            """
            return self._start

        @property
        def tools(self) -> 'HierarchyCrawler.Tools':
            """
            :return: Tools this uses to do its task.
            """
            return self._tools

    @dataclass
    class Tools:
        """Tools this uses to do its job.
        """
        variants: VariantFinder = field(
            default_factory=lambda: VariantFinder()
        )
        """Used to find the parent variant of another variant."""

    def __init__(self, variant: Variant, tools: Optional[Tools] = None):
        """Constructor.

        :param variant: The variant to crawl the hierarchy for.
        :param tools: Tools this uses to do its job.
        """
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
    def variant(self) -> Variant:
        """
        :return: The variant to crawl the hierarchy for.
        """
        return self._variant

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its job.
        """
        return self._tools


class HierarchyCrawlerFactory:
    """Factory for :class:`HierarchyCrawler`.
    """

    def from_variant(self, variant: Variant) -> HierarchyCrawler:
        """Create a new instance from a variant.

        :param variant: The variant to crawl though.
        :return: A new instance.
        """
        return HierarchyCrawler(variant)


class HierarchyBuilder:
    """Gets the whole hierarchy of jobs on top of certain Zuul elements.
    """

    class VariantTask:
        """Gets the hierarchy of jobs on top a variant.
        """

        def __init__(self, variant: Variant, tools: 'HierarchyBuilder.Tools'):
            """Constructor.

            :param variant: Variant to fetch hierarchy for.
            :param tools: Tools this uses to do its job.
            """
            self._variant = variant
            self._tools = tools

        def build(self) -> Sequence[Variant]:
            """Get the hierarchy for the variant targeted by this. Instead
            of a sequence of jobs, this will take care of finding the parent
            on each variant, generating with it a list of variants. Such
            sequence is ordered from the starting variant up to the base
            one. The hierarchy is returned as a :class:`Sequence` to allow
            for it to be inversed.

            :return: The hierarchy.
            """
            crawler = self.tools.crawlers.from_variant(self.variant)

            return [*crawler]

        @property
        def variant(self) -> Variant:
            """
            :return: Variant to fetch hierarchy for.
            """
            return self._variant

        @property
        def tools(self) -> 'HierarchyBuilder.Tools':
            """
            :return: Tools this uses to do its job.
            """
            return self._tools

    @dataclass
    class Tools:
        """Tools this uses to do its job.
        """
        crawlers: HierarchyCrawlerFactory = field(
            default_factory=lambda: HierarchyCrawlerFactory()
        )
        """Used to go through the hierarchy of jobs of a variant."""

    def __init__(self, tools: Optional[Tools] = None):
        """Constructor.

        :param tools: Tools this uses. 'None' to let this build its own.
        """
        if tools is None:
            tools = HierarchyBuilder.Tools()

        self._tools = tools

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its job.
        """
        return self._tools

    def from_variant(self, variant: Variant) -> VariantTask:
        """Starts an action to get the hierarchy of jobs on top of a variant.

        :param variant: The variant to get the hierarchy for.
        :return: The search task.
        """
        return HierarchyBuilder.VariantTask(
            variant=variant,
            tools=self.tools
        )


class RecursiveVariableSearch:
    """Figures out the variables that affect a variant by looking at their
    inheritance from the base job to the bottom one.
    """

    @dataclass
    class Tools:
        """Tools this uses to do its job.
        """
        hierarchy: HierarchyBuilder = field(
            default_factory=lambda: HierarchyBuilder()
        )
        """Used to get the hierarchy of jobs of a variant."""

    def __init__(self, variant: Variant, tools: Optional[Tools] = None):
        """Constructor.

        :param variant: The variant to get the variables for.
        :param tools: Tools this uses to do its job. 'None' to let this
            build its own.
        """
        if tools is None:
            tools = RecursiveVariableSearch.Tools()

        self._variant = variant
        self._tools = tools

    @property
    def variant(self) -> Variant:
        """
        :return: The variant to get the variables for.
        """
        return self._variant

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its job.
        """
        return self._tools

    def search(self) -> Variables:
        """Recursively looks for the variables that affect the variant.

        :return: Dictionary containing the variables.
        """
        result = {}

        hierarchy = self.tools.hierarchy.from_variant(self.variant).build()
        hierarchy = reversed(hierarchy)

        for level in hierarchy:
            result.update(level.variables)

        return result


class RecursiveVariableSearchFactory:
    """Factory for :class:`RecursiveVariableSearch`.
    """

    def from_variant(self, variant: Variant) -> RecursiveVariableSearch:
        """Creates a new instance starting from a variant.

        :param variant: The variant to work with.
        :return: A new instance.
        """
        return RecursiveVariableSearch(variant)
