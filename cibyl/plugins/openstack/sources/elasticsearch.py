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

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source import speed_index
from cibyl.utils.dicts import chunk_dictionary_into_lists
from cibyl.utils.filtering import IP_PATTERN


class ElasticSearch(SourceExtension):
    """Elasticsearch Source"""

    @speed_index({'base': 4})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from elasticsearch server.

        :returns: container of jobs with deployment information from
        elasticsearch server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)
        self.check_jobs_for_spec(jobs_found, **kwargs)

        query_body = {
            # We don't want results in the main hits
            # size 0 don't show it. We will have the results
            # in the aggregations side
            "size": 0,
            "from": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": []
                            }
                        },
                        {
                            "bool": {
                                "should": []
                            }
                        }
                    ]
                }
            },
            # We should GROUP BY job names
            "aggs": {
                "group_by_job_name": {
                    "terms": {
                        "field": "job_name.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "last_build": {
                            # And take the first coincidence
                            "top_hits": {
                                "size": 1,
                                # Sorted by build_num to get the last info
                                "sort": [
                                        {
                                            "build_num": {
                                                "order": "desc"
                                            }
                                        }
                                ],
                                "_source": ['build_url']
                            }
                        }
                    }
                }
            }
        }

        # We can't send a giant query in the request to the elasticsearch
        # for asking to all the jobs information. Instead of doing one
        # query for job we create a list of jobs sublists and do calls
        # divided by chunks. chunk_size_for_search quantity will be
        # the size of every sublist. If we have 2000 jobs we will have
        # the following calls: 2000 / 600 = 3.33 -> 4 calls.
        chunked_list_of_jobs = chunk_dictionary_into_lists(
            jobs_found,
            400
        )

        # We will filter depending of the field we receive
        # in the kwargs
        def append_exists_field_to_query(field: str):
            query_body['query']['bool']['must'][1]['bool']['should'].append(
                {
                    "exists": {
                        "field": field
                    }
                }
            )

        # We will select just the field we receive
        # in the kwargs
        def append_get_specific_field(field: str):
            (query_body['aggs']['group_by_job_name']['aggs']
             ['last_build']['top_hits']['_source'].append(
                 f"{field}"
             ))

        available_spec_fields = [
            'topology',
            'ip_version',
            'dvr',
            'network_backend',
            'overcloud_templates',
            'storage_backend',
            'osp_release',
            'test_setup',
            'test_suites'
        ]

        if 'spec' in kwargs:
            for spec_field in available_spec_fields:
                append_exists_field_to_query(spec_field)
                append_get_specific_field(spec_field)

        if 'topology' in kwargs:
            append_exists_field_to_query('topology')
            append_get_specific_field('topology')
        ip_version_argument = None
        if 'ip_version' in kwargs:
            ip_version_argument = kwargs.get('ip_version').value
            append_exists_field_to_query('ip_version')
            append_get_specific_field('ip_version')
        dvr_argument = None
        if 'dvr' in kwargs:
            dvr_argument = kwargs.get('dvr').value
            append_exists_field_to_query('dvr')
            append_get_specific_field('dvr')
        release_argument = None
        if 'release' in kwargs:
            release_argument = kwargs.get('release').value
            append_exists_field_to_query('osp_release')
            append_get_specific_field('osp_release')
        network_argument = None
        if 'network_backend' in kwargs:
            network_argument = kwargs.get('network_backend').value
            append_exists_field_to_query('network_backend')
            append_get_specific_field('network_backend')
        cinder_backend_argument = None
        if 'cinder_backend' in kwargs:
            cinder_backend_argument = kwargs.get('cinder_backend').value
            append_exists_field_to_query('storage_backend')
            append_get_specific_field('storage_backend')
        test_setup_argument = None
        if 'test_setup' in kwargs:
            test_setup_argument = kwargs.get('test_setup').value
            append_exists_field_to_query('test_setup')
            append_get_specific_field('test_setup')
        overcloud_templates_argument = None
        if 'overcloud_templates' in kwargs:
            user_overcloud_templates = kwargs.get('overcloud_templates')
            overcloud_templates_argument = user_overcloud_templates.value
            overcloud_templates_argument = set(overcloud_templates_argument)
            append_exists_field_to_query('overcloud_templates')
            append_get_specific_field('overcloud_templates')

        hits_info = {}
        for jobs_list in chunked_list_of_jobs:
            for job in jobs_list:
                query_body['query']['bool']['must'][0]['bool']['should'] \
                    .append(
                        {
                            "match": {
                                "job_name.keyword": f"{job}"
                            }
                        }
                    )

            results = self.__query_get_hits(
                query=query_body,
                index='logstash_jenkins_jobs_cibyl'
            )
            for result in results:
                hits_info[
                    result['key']
                ] = result['last_build']['hits']['hits'][0]
            query_body['query']['bool']['must'][0]['bool']['should'].clear()

        job_objects = {}
        for job_name in jobs_found.keys():

            job_source_data = {}
            if job_name in hits_info:
                job_source_data = hits_info[job_name]['_source']

            job_url = jobs_found[job_name].url
            # If data does not exist in the source we
            # don't wanna display it
            topology = job_source_data.get(
                "topology", "")
            network_backend = job_source_data.get(
                "network_backend", "")
            ip_version = job_source_data.get(
                "ip_version", "")
            cinder_backend = job_source_data.get(
                "storage_backend", "")
            dvr = job_source_data.get(
                "dvr", "")
            osp_release = job_source_data.get(
                "osp_release", "")
            overcloud_templates = job_source_data.get(
                "overcloud_templates", None)
            if overcloud_templates:
                # the overcloud templates are returned in a comma separated
                # string, parsed it into a set of templates
                overcloud_templates = overcloud_templates.split(",")
                # infrared stores the overcloud templates as "none" if none are
                # used
                overcloud_templates = {name for name in overcloud_templates if
                                       name != "none"}
            else:
                overcloud_templates = set()
            test_setup = job_source_data.get("test_setup")
            tests_suites = job_source_data.get("test_suites")
            if tests_suites:
                tests_suites = set(tests_suites.split(","))

            if ip_version != '':
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

            # Check if necessary filter by cinder_backend backend:
            if cinder_backend_argument and \
                    cinder_backend not in cinder_backend_argument:
                continue

            # check if necessary filter by test_setup
            if test_setup_argument and test_setup not in test_setup_argument:
                continue

            # check if necessary filter by overcloud_templates, and check if
            # there is any intersection between the used-specified templates
            # and the templates found in the job (if not, skip the job)
            if overcloud_templates_argument and \
                    not (overcloud_templates_argument & overcloud_templates):
                continue

            job_objects[job_name] = Job(name=job_name, url=job_url)
            network = Network(ip_version=ip_version, dvr=dvr,
                              network_backend=network_backend,
                              tls_everywhere='')
            storage = Storage(cinder_backend=cinder_backend)
            ironic = Ironic()
            test_collection = None
            if tests_suites or test_setup or 'spec' in kwargs:
                test_collection = TestCollection(tests_suites, test_setup)
            deployment = Deployment(
                release=osp_release,
                infra_type='',
                nodes={},
                services={},
                topology=topology,
                network=network,
                storage=storage,
                ironic=ironic,
                overcloud_templates=overcloud_templates,
                test_collection=test_collection
            )

            job_objects[job_name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)
