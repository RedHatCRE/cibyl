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

from elasticsearch import Elasticsearch

from cibyl.exceptions.elasticsearch import ElasticSearchError

LOG = logging.getLogger(__name__)


class ElasticSearchClient:  # pylint: disable=too-few-public-methods
    """Elasticsearch client to connect to the instance
    and retrieve the data from this one"""

    def __init__(self: object,
                 host: str = "http://localhost",
                 port: int = 9200) -> None:
        """Initialization of ElasticSearchClient

        :param host: Elasticsearch host including the scheme
        :type host: str, optional
        :param port: Port for sending REST requests to the instance
        :type port: str, optional"""
        self.address = f"{host}:{port}"

    def connect(self: object) -> Elasticsearch:
        """Connects to the elasticsearch instance

        :return: Elasticsearch module instance
        :rtype: Elasticsearch
        :raises: ElasticSearchError:
                 If exists an unhandled connection error
        """
        es_client = Elasticsearch(self.address)
        if not es_client.ping():
            raise ElasticSearchError("Error connecting to Elasticsearch")
        LOG.info("Connection to ElasticSearch successful")
        return es_client
