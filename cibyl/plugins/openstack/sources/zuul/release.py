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


class ReleaseFinder:
    DEFAULT_RELEASE_FIELDS = (
        'rhos_release_version',
        'osp_release',
        'release'
    )

    def __init__(self, search_terms=DEFAULT_RELEASE_FIELDS):
        self._search_terms = search_terms

    @property
    def search_terms(self):
        return self._search_terms

    def find_release_for(self, variant):
        """

        :param variant:
        :type variant: :class:`cibyl.sources.zuul.transactions.VariantResponse`
        :return:
        """
        for search_term in self.search_terms:
            variables = variant.variables(recursive=True)

            if search_term in variables:
                return variables[search_term]

        return 'N/A'
