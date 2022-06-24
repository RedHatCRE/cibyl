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
from typing import Any, Iterable, Optional

from cibyl.sources.zuul.transactions import VariantResponse

LOG = logging.getLogger(__name__)


class FeatureSetFinder:
    @dataclass
    class SearchTerms:
        for_featureset: Iterable[str] = ('featureset',)
        for_overrides: Iterable[str] = ('featureset_override',)

    def __init__(self, search_terms: SearchTerms = SearchTerms()):
        self._search_terms = search_terms

    @property
    def search_terms(self):
        return self._search_terms

    def find_featureset_in(self, variant: VariantResponse) -> Optional[str]:
        LOG.debug("Searching for featureset on variant: '%s'.", variant.name)

        return self._find_in_variables(
            variant=variant,
            search_terms=self.search_terms.for_featureset
        )

    def find_overrides_in(self, variant: VariantResponse) -> Optional[dict]:
        LOG.debug("Searching for overrides on variant: '%s'.", variant.name)

        return self._find_in_variables(
            variant=variant,
            search_terms=self.search_terms.for_overrides
        )

    def _find_in_variables(self,
                           variant: VariantResponse,
                           search_terms: Iterable[str]) -> Optional[Any]:
        variables = variant.variables(recursive=True)

        for search_term in search_terms:
            if search_term in variables:
                return variables[search_term]

        return None
