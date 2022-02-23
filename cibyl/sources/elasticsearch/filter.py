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

import argparse
import logging
from sys import exit

from cibyl.sources.elasticsearch.client import ElasticSearchClient

LOG = logging.getLogger(__name__)


class ElasticSearchOSPFilter:

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
            LOG.error(f"Query error. Details: {e}")
            exit(1)
        return response['hits']['hits']


def parse_arguments() -> object:
    parser = argparse.ArgumentParser(
        description='Tool for filters test results anomalies in order to '
                    'compare them separately from the accepted delta range.')
    parser.add_argument('--host',
                        help='Elasticsearch host including scheme',
                        type=str,
                        default="http://localhost",
                        dest='host')
    parser.add_argument('--port',
                        help='Elasticsearch port for sending REST requests',
                        type=int,
                        default=9200,
                        dest='port')
    parser.add_argument('--index',
                        help='Index for searching queries',
                        required=True,
                        dest='index')
    parser.add_argument('--type',
                        help='Type of search. String or regex string',
                        type=str,
                        choices=['string', 'regex'],
                        required=True,
                        dest='type')
    parser.add_argument('--key',
                        help='key',
                        required=True,
                        dest='key')
    parser.add_argument('--value',
                        help='value',
                        required=True,
                        dest='value')
    return parser.parse_args()


def main():
    args = parse_arguments()
    elastic_client = ElasticSearchClient(args.host, args.port).connect()
    elastic_filter = ElasticSearchOSPFilter(elastic_client)
    query_data = {
        'index': args.index,
        'type': args.type,
        'key': args.key,
        'value': args.value,
    }
    if query_data['type'] == 'string':
        elastic_filter.get_job_by_name(query_data)
    else:
        elastic_filter.get_jobs_by_regex(query_data)


if __name__ == "__main__":
    main()
