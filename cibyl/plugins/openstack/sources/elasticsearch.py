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
import re

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.sources.source import speed_index
from cibyl.utils.filtering import IP_PATTERN

LOG = logging.getLogger(__name__)


class ElasticSearch:
    """Elasticsearch Source"""

    @speed_index({'base': 2})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from elasticsearch server.

        :returns: container of jobs with deployment information from
        elasticsearch server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)

        query_body = {
            "query": {
              "bool": {
                "must": [
                  {
                    "bool": {
                      "must": []
                    }
                  },
                  {
                    "bool": {
                      "should": [
                        {
                          "exists": {
                            "field": "ip_version"
                          }
                        },
                        {
                          "exists": {
                            "field": "storage_backend"
                          }
                        },
                        {
                          "exists": {
                            "field": "network_backend"
                          }
                        },
                        {
                          "exists": {
                            "field": "dvr"
                          }
                        },
                        {
                          "exists": {
                            "field": "topology"
                          }
                        }
                      ],
                      "minimum_should_match": 1
                    }
                  }
                ]
              }
            },
            "size": 1,
            "sort": [
                {
                    "timestamp.keyword": {
                        "order": "desc"
                    }
                }
            ]
        }

        results = []
        hits = []
        for job in jobs_found:
            query_body['query']['bool']['must'][0]['bool']['must'] = {
                "match": {
                    "job_name.keyword": f"{job}"
                }
            }
            results = self.__query_get_hits(
                query=query_body,
                index='logstash_jenkins'
            )
            if results:
                hits.append(results[0])

        if not results:
            return jobs_found

        ip_version_argument = None
        if 'ip_version' in kwargs:
            ip_version_argument = kwargs.get('ip_version').value
        dvr_argument = None
        if 'dvr' in kwargs:
            dvr_argument = kwargs.get('dvr').value
        release_argument = None
        if 'release' in kwargs:
            release_argument = kwargs.get('release').value
        network_argument = None
        if 'network_backend' in kwargs:
            network_argument = kwargs.get('network_backend').value
        storage_argument = None
        if 'storage_backend' in kwargs:
            storage_argument = kwargs.get('storage_backend').value
        if 'osp_release' in kwargs:
            storage_argument = kwargs.get('osp_release').value

        job_objects = {}
        for hit in hits:
            job_name = hit['_source']['job_name']
            job_url = re.compile(r"(.*)/\d").search(
                hit['_source']['build_url']
            ).group(1)

            # If the key exists assign the value otherwise assign unknown
            topology = hit['_source'].get(
                "topology", "unknown")
            network_backend = hit['_source'].get(
                "network_backend", "unknown")
            ip_version = hit['_source'].get(
                "ip_version", "unknown")
            storage_backend = hit['_source'].get(
                "storage_backend", "unknown")
            dvr = hit['_source'].get(
                "dvr", "unknown")
            osp_release = hit['_source'].get(
                "osp_release", "unknown")

            if ip_version != 'unknown':
                matches = IP_PATTERN.search(ip_version)
                ip_version = matches.group(1)

            # Check if necessary filter by IP version:
            if ip_version_argument and \
                    ip_version not in ip_version_argument:
                continue

            # Check if necessary filter by dvr:
            if isinstance(dvr_argument, list) and \
                    dvr not in dvr_argument:
                continue

            # Check if necessary filter by release version:
            if release_argument and \
                    osp_release not in release_argument:
                continue

            # Check if necessary filter by network backend:
            if network_argument and \
                    network_backend not in network_argument:
                continue

            # Check if necessary filter by storage backend:
            if storage_argument and \
                    storage_backend not in storage_argument:
                continue

            job_objects[job_name] = Job(name=job_name, url=job_url)
            deployment = Deployment(
                release=osp_release,
                infra_type='',
                nodes={},
                services={},
                ip_version=ip_version,
                topology=topology,
                network_backend=network_backend,
                dvr=dvr,
                storage_backend=storage_backend,
                tls_everywhere=''
            )

            job_objects[job_name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)
