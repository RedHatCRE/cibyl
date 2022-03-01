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


class ElasticSearchOSP:

    def __init__(self: object, elastic_client: object) -> None:
        self.es = elastic_client

    def get_job_by_name(self: object, query_data: dict):
        """Get all the job information with an exact match

        :param query_data: Information required for the query:
                Index, Search key and Search Value.
        :type query_data: dict
        """
        query_body = {
           'query': {
                'term': {
                    f"{query_data['key']}.keyword": {
                        'value': query_data['value']
                    }
                }
            }
        }
        hits = self.__query_get_hits(query_data['index'], query_body)
        return hits

    def get_jobs_by_regex(self: object, query_data: dict):
        """Get all the jobs that match the provided regex string

        :param query_data: Information required for the query:
                Index, Search key and Search Value.
        :type query_data: dict
        """
        query_body = {
            'query': {
                'regexp': {
                    query_data['key']: {
                        'value': query_data['value']
                    }
                }
            }
        }
        hits = self.__query_get_hits(query_data['index'], query_body)
        return hits

    def __query_get_hits(self: object, index: str, query: dict) -> list:
        """This method is used to perform the search query to ElasticSearch
        and get all the hits

        :param index: Index
        :type index: str
        :param query: Index and query to perform
        :type query: dict
        :return: List of hits.
        """
        try:
            response = self.es.search(
                index=index,
                body=query
            )
        except Exception as e:
            error_message = f"Query error. Details: {e}"
            LOG.error(error_message)
            raise ElasticSearchError(error_message)
        return response['hits']['hits']
