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
# pylint: disable=no-member, protected-access
import os
import shutil
from unittest import TestCase
from unittest.mock import Mock, patch

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.sources.jenkins_job_builder import JenkinsJobBuilder


def remove_fake_files():
    """Remove the fake xml files."""
    shutil.rmtree("out_jjb_test")


def fake_xml_files():
    """Create two fake xml files to test the get_jobs method."""
    path1 = "out_jjb_test/out-xml/fake_job1"
    path2 = "out_jjb_test/out-xml/fake_job2"
    os.makedirs(path1, exist_ok=True)
    os.makedirs(path2, exist_ok=True)
    file_name = os.path.join(path1, "config.xml")
    with open(file_name, "w", encoding="utf-8") as fake1:
        fake1.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fake1.write('<com.folder.Folder plugin="cloudbees-folder">\n')
        fake1.write('  <icon class="com.folder.icons.StockFolderIcon"/>\n')
        fake1.write('  <views/>\n')
        fake1.write('  <scm class="hudson.scm.NullSCM"/>\n')
        fake1.write('  <publishers/>\n')
        fake1.write('  <buildWrappers/>\n')
        fake1.write('</com.folder.Folder>\n')

    file_name = os.path.join(path2, "config.xml")
    with open(file_name, "w", encoding="utf-8") as fake2:
        fake2.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fake2.write('<flow-definition plugin="workflow-job">\n')
        fake2.write('  <definition plugin="workflow-cps" class="org.j">\n')
        fake2.write('  </definition>\n')
        fake2.write('</flow-definition> \n')


@patch('cibyl.sources.jenkins_job_builder.JenkinsJobBuilder.get_repo')
class TestJenkinsJobBuilderSource(TestCase):
    """Tests for :class:`JenkinsJobBuilder`."""
    def setUp(self):
        fake_xml_files()

    def tearDown(self):
        remove_fake_files()

    # second argument is necessary to support patching of mock get_repo method
    def test_with_all_args(self, _):
        """Checks that the object is built correctly when all arguments are
        provided.
        """
        url = 'url/to/repo'
        dest = 'dest_folder'
        branch = 'master'

        jenkins = JenkinsJobBuilder(url, dest=dest, branch=branch)

        self.assertEqual(dest, jenkins.dest)
        self.assertEqual(url, jenkins.url)
        self.assertEqual(branch, jenkins.branch)

    def test_with_no_dest(self, _):
        """Checks that object is built correctly when the dest is not
        provided.
        """
        url = 'url/to/repo/'
        branch = 'master'

        jenkins = JenkinsJobBuilder(url, branch=branch)

        self.assertEqual(url, jenkins.url)
        self.assertEqual(branch, jenkins.branch)
        self.assertIsNotNone(jenkins.dest)
        self.assertTrue(os.path.isdir(jenkins.dest))

    def test_with_no_branch(self, _):
        """Checks that object is built correctly when the branch is not
        provided.
        """
        url = 'url/to/repo/'
        dest = 'dest'

        jenkins = JenkinsJobBuilder(url, dest=dest)

        self.assertEqual(url, jenkins.url)
        self.assertIsNone(jenkins.branch)
        self.assertEqual(dest, jenkins.dest)

    def test_get_jobs(self, _):
        """
            Tests that the internal logic of :meth:`JenkinsJobBuilder.get_jobs`
            is correct. The jenkins API method that should do the query is
            mocked so that it returns the query itself.
        """
        jenkins = JenkinsJobBuilder("url", dest="out_jjb_test")
        jenkins._generate_xml = Mock()

        jobs = jenkins.get_jobs(jobs=["*"])
        job = Job(name="fake_job2")
        result = AttributeDictValue("jobs", attr_type=Job,
                                    value={"fake_job2": job})

        self.assertEqual(jobs, result)
