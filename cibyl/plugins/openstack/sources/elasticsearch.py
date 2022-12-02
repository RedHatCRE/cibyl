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

from typing import Dict, Iterable

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.ironic import Ironic
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.storage import Storage
from cibyl.plugins.openstack.test_collection import TestCollection
from cibyl.sources.elasticsearch.api import filter_jobs
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source import speed_index
from cibyl.utils.filtering import IP_PATTERN


def keep_only_last_build_hit(hits: Iterable[dict]) -> Dict[str, dict]:
    """
        Filter the hits obtained from an elasticsearch query so that we only
        keep the latest build for each job. The documents are returned in
        a dictionary with job_name: document structure.
        :returns: The document corresponding to the latest build for each job
    """
    final_hits = {}
    for hit in hits:
        job_name = hit["job_name"]
        if job_name not in final_hits:
            final_hits[job_name] = hit
        else:
            max_build = final_hits[job_name]["build_num"]
            current_build = hit["build_num"]
            if current_build > max_build:
                final_hits[job_name] = hit
    return final_hits


class ElasticSearch(SourceExtension):
    """Elasticsearch Source"""

    @speed_index({'base': 4})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from elasticsearch server.

        :returns: container of jobs with deployment information from
        elasticsearch server
        :rtype: :class:`AttributeDictValue`
        """

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

        fields_to_request = set()
        if 'spec' in kwargs:
            fields_to_request = set(available_spec_fields)

        if 'topology' in kwargs:
            fields_to_request.add('topology')

        ip_version_argument = None
        if 'ip_version' in kwargs:
            ip_version_argument = kwargs.get('ip_version').value
            fields_to_request.add('ip_version')

        dvr_argument = None
        if 'dvr' in kwargs:
            dvr_argument = kwargs.get('dvr').value
            fields_to_request.add('dvr')

        release_argument = None
        if 'release' in kwargs:
            release_argument = kwargs.get('release').value
            fields_to_request.add('osp_release')

        network_argument = None
        if 'network_backend' in kwargs:
            network_argument = kwargs.get('network_backend').value
            fields_to_request.add('network_backend')

        cinder_backend_argument = None
        if 'cinder_backend' in kwargs:
            cinder_backend_argument = kwargs.get('cinder_backend').value
            fields_to_request.add('storage_backend')

        test_setup_argument = None
        if 'test_setup' in kwargs:
            test_setup_argument = kwargs.get('test_setup').value
            fields_to_request.add('test_setup')

        overcloud_templates_argument = None
        if 'overcloud_templates' in kwargs:
            user_overcloud_templates = kwargs.get('overcloud_templates')
            overcloud_templates_argument = user_overcloud_templates.value
            overcloud_templates_argument = set(overcloud_templates_argument)
            fields_to_request.add('overcloud_templates')

        # Empty query for all hits or elements
        query_body = {
            "query": {
                "match_all": {}
                },
            "_source": ["job_name", "job_url",
                        "build_num"]+list(fields_to_request)
        }

        hits = self.__query_get_hits(
            query=query_body,
            index='logstash_jenkins_jobs_cibyl'
        )
        # make the hits list a flat list of dicts with the job information for
        # easier filtering
        hits = [hit['_source'] for hit in hits]
        hits = filter_jobs(hits, **kwargs)
        hits = keep_only_last_build_hit(hits)
        self.check_jobs_for_spec(hits, **kwargs)

        job_objects = {}
        for job_name, job_source_data in hits.items():

            job_url = job_source_data['job_url']

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
