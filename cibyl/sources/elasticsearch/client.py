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
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout
from sys import exit


LOG = logging.getLogger(__name__)


class ElasticSearchClient:

    def __init__(self: object,
                 host: str = "http://localhost",
                 port: int = 9200) -> None:
        self.address = f"{host}:{port}"

    def connect(self: object) -> Elasticsearch:
        """This is used for connecting to the ElasticSearch instance.

        :param host: Elasticsearch host including the scheme
        :type host: str, optional
        :param port: Port for sending REST requests to the instance
        :type port: str, optional
        :return: Elasticsearch module instance
        :rtype: Elasticsearch
        :raises: ConnectionTimeout:
                 If the connection attempt reach the max time
        :raises: ConnectionError:
                 If exists an handled connection error
        :raises: Exception:
                 If exists an unhandled connection error
        """
        try:
            es = Elasticsearch(self.address)
            es.ping()
        except ConnectionTimeout as e:
            LOG.error(f"Timeout connection to ElasticSearch. Details: {e}")
            exit(1)
        except ConnectionError as e:
            LOG.error(f"Connection error to ElasticSearch. Details: {e}")
            exit(1)
        except Exception as e:
            LOG.error(f"An unknown error occurred connecting to ElasticSearch. \
                        Details: {e}")
            exit(1)
        LOG.info("Connection to ElasticSearch successful")
        return es
