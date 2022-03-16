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
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.sources.elasticsearch.client import ElasticSearchClient
from cibyl.sources.source import Source

LOG = logging.getLogger(__name__)


class ElasticSearchOSP(Source):  # pylint: disable=too-few-public-methods
    """Used to perform queries in elasticsearch"""

    def __init__(self: object, **kwargs) -> None:
        if 'elastic_client' in kwargs:
            self.es_client = kwargs.get('elastic_client')
        else:
            self.es_client = ElasticSearchClient(
                host=kwargs.get('host'),
                port=kwargs.get('port'),
            ).connect()

    def get_jobs(self: object, **kwargs) -> list:
        """Get jobs from elasticsearch

            :returns: Job objects queried from elasticserach
            :rtype: :class:`AttributeDictValue`
        """

        query_body = {
            'query': {
                'match': {
                    'jobName': kwargs.get('jobs').value[0]
                }
            }
        }

        hits = self.__query_get_hits(query_body)

        job_objects = {}

        for hit in hits:
            job_name = hit['_source']['jobName']
            url = hit['_source']['envVars']['BUILD_URL']
            job_objects[job_name] = Job(name=job_name, url=url)
        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

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
                body=query,
                size=1000
            )
        except Exception as exception:
            raise ElasticSearchError("Error getting the results") \
                  from exception
        return response['hits']['hits']
