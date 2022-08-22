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
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter
from string import Template

import yaml

# flake8: noqa E122

TEST_BLOCK_TEMPLATE = Template("""
    <hudson.tasks.junit.TestResultAction plugin="junit@1119.1121.vc43d0fc455">
      <descriptions class="concurrent-hash-map"/>
      <failCount>$FAIL_COUNT</failCount>
      <skipCount>$SKIP_COUNT</skipCount>
      <totalCount>$TOTAL_COUNT</totalCount>
      <healthScaleFactor>1.0</healthScaleFactor>
      <testData/>
    </hudson.tasks.junit.TestResultAction>""")

JUNIT_TEMPLATE = Template(
"""<?xml version='1.1' encoding='UTF-8'?>
<result plugin="junit@1.54">
  <suites>
    <suite>
      <file>file_name</file>
      <name>name</name>
      <duration>985.444</duration>
      <time>985.444</time>
      <nodeId>464</nodeId>
      <enclosingBlocks>
        <string>442</string>
      </enclosingBlocks>
      <enclosingBlockNames>
        <string>Finally Steps</string>
      </enclosingBlockNames>
      <cases>$CASES
      </cases>
    </suite>
  </suites>
  <duration>985.444</duration>
  <keepLongStdio>false</keepLongStdio>
</result>
""")

CASE_TEMPLATE = Template(
"""
        <case>
          <duration>$DURATION</duration>
          <className>$CLASS_NAME</className>
          <testName>$TEST_NAME</testName>
          <skipped>$SKIPPED</skipped>$SKIPPED_MESSAGE$ERROR_TRACE
          <failedSince>0</failedSince>
        </case>""")

BUILD_TEMPLATE = Template("""<?xml version='1.1' encoding='UTF-8'?>
<build>
  <actions>
    <hudson.model.CauseAction>
      <causeBag class="linked-hash-map">
        <entry>
          <hudson.model.Cause_-UserIdCause/>
          <int>1</int>
        </entry>
      </causeBag>
    </hudson.model.CauseAction>$TEST_BLOCK
  </actions>
  <queueId>1</queueId>
  <timestamp>1660119863992</timestamp>
  <startTime>1660119864008</startTime>
  <result>$RESULT</result>
  <description>$DESCRIPTION</description>
  <duration>22</duration>
  <charset>UTF-8</charset>
  <keepLog>false</keepLog>
  <builtOn></builtOn>
  <workspace>/var/jenkins_home/$JOB_NAME/workspace</workspace>
  <hudsonVersion>2.332.3</hudsonVersion>
  <scm class="hudson.scm.NullChangeLogParser"/>
  <culprits class="java.util.Collections$UnmodifiableSet">
    <c class="sorted-set"/>
  </culprits>
</build>""")


def parse_args():
    program_help = "Read a configuration yaml file and create a 'jobs' folder"
    program_help += " for a Jenkins instance with said configuration.\n"
    program_help += "Program must run from the root of the cibyl repo. The"
    program_help += " configuration is a yaml file with the structure:\n"
    program_help += """
    job1:
        build1:
            description: "description string"
            result: "SUCCESS"
            test1:
              - name: "test_case1"
                class_name: "class_test_1"
                duration: "0.5"
                result: "FAILED"
    job2:
        build1:
            # build with no tests and default values for result (SUCCESS) and
            # duration (0.001s)
            description: "Test description"

    job3: # job with no builds"""

    parser = ArgumentParser(description=program_help,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('environment', type=str,
                        help="Yaml file describing the jenkins environment")
    parser.add_argument('output_folder', help="Path to store the output",
                        type=str)
    return parser.parse_args()


def prepare_job_folders(job_folder, builds_folder, builds):
    """Create the files corresponding to a job read from the
    environment file."""
    os.makedirs(job_folder, exist_ok=True)
    os.makedirs(builds_folder, exist_ok=True)
    with open(os.path.join(job_folder, "nextBuildNumber"), "w") as fw:
        fw.write(f"{len(builds)+1}\n")
    config = "tests/cibyl/e2e/data/images/jenkins/jobs/basic-job-config.xml"
    shutil.copy(config,
                os.path.join(job_folder, "config.xml"))
    os.makedirs(f"{job_folder}/workspace", exist_ok=True)


def create_test(test):
    """Create the files corresponding to a test case read from the environment
    file."""
    test_result = test.get("result", "SUCCESS")
    test_name = test.get("name")
    test_class = test.get("class_name", "class_test")
    test_duration = test.get("duration", "0.001")
    skipped = "true" if test_result == "SKIPPED" else "false"
    is_skipped = False
    is_failed = False
    if skipped == "true":
        skipped_message = "\n          <skippedMessage>Some reason"
        skipped_message += " to skip</skippedMessage>"
        is_skipped = True
    else:
        is_skipped = False
        skipped_message = ""
    if test_result in ("FAILED", "FAILURE"):
        is_failed = True
        error_trace = "\n          <errorStackTrace>Some reason"
        error_trace += " to fail</errorStackTrace>"
    else:
        error_trace = ""
    case_info = {"DURATION": test_duration,
                 "CLASS_NAME": test_class, "TEST_NAME": test_name,
                 "SKIPPED": skipped, "SKIPPED_MESSAGE": skipped_message,
                 "ERROR_TRACE": error_trace}
    return CASE_TEMPLATE.substitute(case_info), is_skipped, is_failed


def create_build(builds_folder, build, build_info, job):
    """
    Create the file corresponding to a build read from the environment file.
    The files create are a log, changelog.xml, the build.xml with the build
    configuration and the junitResult.xml with the testing information (if
    applicable).
    """
    build_folder = os.path.join(builds_folder, build)
    os.makedirs(build_folder, exist_ok=True)
    result = build_info.get("result", "SUCCESS")
    build_description = build_info.get("description", "custom description")
    is_success = (result == "SUCCESS")
    with open(f"{build_folder}/log", "w") as fw:
        fw.write("Started by user unknown or anonymous\n")
        fw.write("Running as SYSTEM\n")
        fw.write(f"Building in workspace /var/jenkins_home/workspace/{job}\n")
        fw.write(f"Finished: {result}\n")

    with open(f"{build_folder}/changelog.xml", "w") as fw:
        fw.write("<log/>\n")
    tests = build_info.get("tests", {})
    tests_block = ""
    junit_cases = []
    if tests:
        skip_count = 0
        fail_count = 0
        total_count = len(tests)
        for test in tests:
            test_case, skipped, failed = create_test(test)
            if skipped:
                skip_count += 1
            if failed:
                fail_count += 1
            junit_cases.append(test_case)

        tests_block = TEST_BLOCK_TEMPLATE.substitute(FAIL_COUNT=fail_count,
                                                     SKIP_COUNT=skip_count,
                                                     TOTAL_COUNT=total_count)
        with open(os.path.join(build_folder, "junitResult.xml"), "w") as fw:
            junit_cases = ''.join(junit_cases)
            fw.write(f"{JUNIT_TEMPLATE.substitute(CASES=junit_cases)}\n")

    with open(f"{build_folder}/build.xml", "w") as fw:
        build_config = BUILD_TEMPLATE.safe_substitute(
                RESULT=result,
                DESCRIPTION=build_description, JOB_NAME=job,
                TEST_BLOCK=tests_block)
        fw.write(f"{build_config}\n")
    return is_success


def main(env_file, output_folder):
    """Parse the environment file and create the 'jobs' folder for the jenkins
    instance."""
    os.makedirs(output_folder, exist_ok=True)
    with open(env_file) as yaml_data:
        environment = yaml.safe_load(yaml_data)
    jobs_folder = os.path.join(output_folder, "jobs")
    os.makedirs(jobs_folder, exist_ok=True)
    for job, builds in environment.items():
        if builds is None:
            # handle the case for jobs without builds
            builds = {}
        job_folder = os.path.join(jobs_folder, job)
        builds_folder = os.path.join(job_folder, "builds")
        prepare_job_folders(job_folder, builds_folder, builds)
        last_successful_build = 0
        for build, build_info in builds.items():
            is_successful_build = create_build(builds_folder, build,
                                               build_info, job)
            if is_successful_build:
                last_successful_build = build

        last_completed_build = len(builds)
        with open(os.path.join(builds_folder, "permalinks"), "w") as fw:
            fw.write(f"lastCompletedBuild {last_completed_build}\n")
            fw.write(f"lastStableBuild {last_successful_build}\n")
            fw.write(f"lastSuccessfulBuild {last_successful_build}\n")


if __name__ == "__main__":
    args = parse_args()
    main(args.environment, args.output_folder)
