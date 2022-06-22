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
from typing import List, Optional

from cibyl.sources.zuul.transactions import VariantResponse

LOG = logging.getLogger(__name__)


class ReleaseFinder:
    """Utility meant to make finding the release of a job easier.
    """
    DEFAULT_RELEASE_FIELDS = (
        'rhos_release_version',
        'osp_release',
        'release'
    )
    """Default variables known to hold the job's release."""

    def __init__(self,
                 search_terms: List[str] = DEFAULT_RELEASE_FIELDS) -> None:
        """Constructor.

        :param search_terms: List containing the names of the job variables
            that point to the job's RHOS target release.
        :type search_terms: list[str]
        """
        self._search_terms = search_terms

    @property
    def search_terms(self) -> List[str]:
        """
        :return: List of variables that this will search through to find
            the release.
        :rtype: list[str]
        """
        return self._search_terms

    def find_release_for(self, variant: 'VariantResponse') -> Optional[str]:
        """Gets the RHOS target release from a job variant.

        This will take care of going through the variant's variables as well
        as those from all its parents until it finds one of the search terms
        known by this. Take note that this will give higher priority to search
        terms that appear sooner on the list. Meaning that if 'var1' is the
        first term on the list, its value will be returned first even if other
        terms are also present.

        :param variant: The variant to consult.
        :type variant: :class:`cibyl.sources.zuul.transactions.VariantResponse`
        :return: The release if it was found, None if not.
        :rtype: str or None
        """
        LOG.debug("Searching for release on variant: '%s'.", variant.name)

        variables = variant.variables(recursive=True)

        for search_term in self.search_terms:
            if search_term in variables:
                return str(variables[search_term])

        return None
