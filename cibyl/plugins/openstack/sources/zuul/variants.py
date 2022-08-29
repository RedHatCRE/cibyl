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
from typing import Any, Iterable, Optional, Tuple

from overrides import overrides

from cibyl.sources.zuul.transactions import VariantResponse
from cibyl.sources.zuul.utils.variants.hierarchy import \
    RecursiveVariableSearchFactory

LOG = logging.getLogger(__name__)


class VariableSearch:
    """Utility meant to make finding a variable in a Zuul job easier.
    """

    @dataclass
    class Tools:
        """Tools this class uses to do its job.
        """
        variables: RecursiveVariableSearchFactory = field(
            default_factory=lambda: RecursiveVariableSearchFactory()
        )
        """Gets all the variables that affect a certain variant."""

    def __init__(
        self,
        search_terms: Iterable[str],
        tools: Optional[Tools] = None
    ):
        """Constructor.

        :param search_terms: List containing the possible names of the job
            variable to be searched. The list will be iterated following the
            containers iterator, giving priority to terms that appear first.
            As an example, given a list of two names for a variable: ['val1',
            'val2'], 'val1' will always be preferred over 'val2', falling back
            to the later one only if the first does not exist.
        :param tools: Tools this uses to do its job. 'None' to let this
            generate its own.
        """
        if tools is None:
            tools = VariableSearch.Tools()

        self._search_terms = search_terms
        self._tools = tools

    @property
    def search_terms(self) -> Iterable[str]:
        """
        :return: Possible names of the desired variable that this will
            search for.
        """
        return self._search_terms

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its job.
        """
        return self._tools

    def search(self, variant: VariantResponse) -> Optional[Tuple[str, Any]]:
        """Search the target variable among the ones defined on the
        provided variant.

        :param variant: The variant to search.
        :return: The name of the found variable next to its value. None if
            the variable was not found.
        """
        variables = self.tools.variables.from_variant(variant).search()

        for search_term in self.search_terms:
            if search_term in variables:
                return search_term, variables[search_term]

        return None


class ReleaseSearch(VariableSearch):
    """Utility designed to make finding the release variable of a job easier.
    """
    DEFAULT_SEARCH_TERMS = (
        'rhos_release_version',
        'osp_release',
        'release'
    )
    """Default variables known to hold the job's release."""

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, str]]:
        LOG.debug("Searching for release on variant: '%s'.", variant.name)

        result = super().search(variant)

        # The release was not found
        if not result:
            return None

        variable, value = result

        return variable, str(value)


class ReleaseNameSearch(VariableSearch):
    """Utility designed to make finding the release name variable of a job
    easier.
    """
    DEFAULT_SEARCH_TERMS = ('release',)
    """Default variables known to hold the job's release name."""

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, str]]:
        LOG.debug("Searching for release name on variant: '%s'.", variant.name)

        return super().search(variant)


class FeatureSetSearch(VariableSearch):
    """Utility designed to make finding the featureset variable of a job
    easier.
    """

    DEFAULT_SEARCH_TERMS = ('featureset',)
    """Default variables known to hold the job's featureset."""

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, str]]:
        LOG.debug("Searching for featureset on variant: '%s'.", variant.name)

        return super().search(variant)


class FeatureSetOverridesSearch(VariableSearch):
    """Utility designed to make finding the featureset overrides of a job
    easier.
    """
    DEFAULT_SEARCH_TERMS = ('featureset_override',)
    """Default variables known to hold the job's featureset overrides."""

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, dict]]:
        LOG.debug("Searching for overrides on variant: '%s'.", variant.name)

        return super().search(variant)


class NodesSearch(VariableSearch):
    """Utility designed to make finding the nodes for a job easier.
    """
    DEFAULT_SEARCH_TERMS = ('nodes',)

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, str]]:
        LOG.debug("Searching for nodes on variant: '%s'.", variant.name)

        return super().search(variant)


class InfraTypeSearch(VariableSearch):
    """Utility designed to make finding the infra type for a job
    easier.
    """
    DEFAULT_SEARCH_TERMS = ('environment_type',)

    def __init__(
        self,
        search_terms: Iterable[str] = DEFAULT_SEARCH_TERMS,
        tools: Optional[VariableSearch.Tools] = None
    ):
        """Constructor. See parent for more information.
        """
        super().__init__(search_terms, tools)

    @overrides
    def search(self, variant: VariantResponse) -> Optional[Tuple[str, str]]:
        LOG.debug("Searching for infra_type on variant: '%s'.", variant.name)

        return super().search(variant)
