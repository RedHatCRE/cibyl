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
from click.testing import CliRunner

from cibyl.cli.main import DEFAULT_CONFIG_PATH, main


class TestMain:
    """ Testing cli.main module """
    def test_main(self):
        """ Test main function """
        runner = CliRunner()
        result = runner.invoke(main, ['-d', '-vv'])
        assert result.output == "Usage: main [OPTIONS] COMMAND [ARGS]...\n"\
                                "Try 'main --help' for help.\n\n"\
                                "Error: Missing command.\n"

    def test_query(self):
        """ Test query function """
        runner = CliRunner()
        result = runner.invoke(main, ['query'])
        assert result.output == "Query: Using config file: {}\n"\
                                "List tests: None\n".format(
                                    DEFAULT_CONFIG_PATH)

    def test_update_db(self):
        """ Test update_db function """
        runner = CliRunner()
        result = runner.invoke(main, ['update-db'])
        assert result.output == "Update-db: Using config "\
                                "file: {}\n".format(DEFAULT_CONFIG_PATH)
