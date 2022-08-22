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
import os
from argparse import ArgumentParser, RawTextHelpFormatter

import yaml

import tests.cibyl.unit.plugins.openstack.sources.test_jenkins as test_utils


def parse_args():
    program_help = "Read a configuration yaml file and create an 'infrared'"
    program_help += " folder for a mock logs server of a Jenkins instance.\n"
    program_help += "The configuration is a yaml file with the structure:\n"
    program_help += """
    job1:
        build1:
            test_suites:
                - "octavia"
                - "neutron"
            setup: "rpm"
            overcloud:
                release: "17.1"
                ip: "4"
                network_backend: "geneve"
                dvr: false
                ml2_driver: ovn
            topology: "compute:2,controller:3"
    job2:
        build1:
            overcloud:
                release: "16.2"
                cinder_backend: "swift"
                tls_everywhere: true
                infra_type: "ovb"
                ironic_inspector: true
                cleaning_network: true

    job3: # job with no builds"""

    parser = ArgumentParser(description=program_help,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('environment', type=str,
                        help="Yaml file describing the openstack environment")
    parser.add_argument('output_folder', help="Path to store the output",
                        type=str)
    return parser.parse_args()


def write_tests(build_folder, build_info):
    """Write the test.yml with testing information for a build."""
    test_file = os.path.join(build_folder, "test.yml")
    test_suites = build_info.get("test_suites")
    setup = build_info.get("setup")
    with open(test_file, "w") as fw:
        fw.write(f"{test_utils.get_yaml_tests(test_suites, setup)}\n")


def write_overcloud_install(build_folder, build_info):
    """Write the overcloud-install.yml with deployment information for
    a build."""
    overcloud_file = os.path.join(build_folder, "overcloud-install.yml")
    deployment = test_utils.get_yaml_overcloud(**build_info["overcloud"])
    with open(overcloud_file, "w") as fw:
        fw.write(f"{deployment}\n")


def create_build(job_folder, build, build_info):
    """
    Create the folders for a build, the infrared folder and the yaml files with
    information inside.
    """
    build_folder = os.path.join(job_folder, build, "infrared")
    os.makedirs(build_folder, exist_ok=True)
    provision_file = os.path.join(build_folder, "provision.yml")
    topology = build_info.get("topology")
    with open(provision_file, "w") as fw:
        fw.write(f"{test_utils.get_yaml_from_topology_string(topology)}\n")
    write_overcloud_install(build_folder, build_info)
    write_tests(build_folder, build_info)


def main(env_file, output_folder):
    """Parse the environment file and create the 'jobs' folder for the jenkins
    instance."""
    os.makedirs(output_folder, exist_ok=True)
    with open(env_file) as yaml_data:
        environment = yaml.safe_load(yaml_data)
    for job, builds in environment.items():
        if builds is None:
            # handle the case for jobs without builds
            builds = {}
        job_folder = os.path.join(output_folder, job)
        os.makedirs(job_folder, exist_ok=True)
        for build, build_info in builds.items():
            create_build(job_folder, build, build_info)


if __name__ == "__main__":
    args = parse_args()
    main(args.environment, args.output_folder)
