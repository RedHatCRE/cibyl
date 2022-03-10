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

from cibyl.exceptions.elasticsearch import ElasticSearchError

LOG = logging.getLogger(__name__)


class ElasticSearchOSP:  # pylint: disable=too-few-public-methods
    """Used to perform queries in elasticsearch"""

    ALLOWED_QUERIES = [
        'regexp',
        'term'
    ]

    def __init__(self: object, elastic_client: object) -> None:
        self.es_client = elastic_client

    def get_jobs_by_name(self: object,
                         job_name: str,
                         query_type: str = 'term') -> list:
        """Get jobs by kind of query
        It can be term (literal search) or regexp

        :param query_type: Kind of query.
                It could be 'term' or 'regexp'
        :type query_data: str
        :param job_name: Name of the job to serch. Literal or regex.
        :type job_name: str
        :return: hits
        :rtype: list
        """

        if query_type not in self.ALLOWED_QUERIES:
            raise ElasticSearchError(f"Query '{query_type}' not allowed. \
                  Allowed queries: {' '.join(self.ALLOWED_QUERIES)}")

        if query_type == 'term':
            key = 'jobName.keyword'
        else:
            key = 'jobName'

        query_body = {
            'query': {
                query_type: {
                    key: {
                        'value': job_name
                    }
                }
            }
        }
        hits = self.__query_get_hits(query_body)
        return hits

    def __query_get_hits(self: object, query: dict, index: str = '') -> list:
        """Perform the search query to ElasticSearch
        and return all the hits

        :param query: Query to perform
        :type query: dict
        :param index: Index
        :type index: str
        :return: List of hits.
        """
        try:
            response = self.es_client.search(
                index=index,
                body=query
            )
        except Exception as exception:
            raise ElasticSearchError("Error getting the results") \
                  from exception
        return response['hits']['hits']
