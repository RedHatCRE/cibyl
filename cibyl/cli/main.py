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
from dataclasses import asdict, dataclass
from typing import Any, Dict

import click

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'),
                                   '.config/cibyl.conf')


@dataclass
class Config():
    """
    Represent config class which hold all the loaded configuration
    """

    name: str
    arg_type: object
    description: str

    def __setattr__(self, name, value):
        """
        Setting values dynamically to the class
        """
        if name is not None and value is not None:
            self.__dict__[name] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Return values stored in dict format
        """
        return {k: v for k, v in asdict(self).items() if v}


@click.group()
@click.option('-d', '--debug', help='Enable debug', is_flag=True)
@click.option('-v', '--verbose', count=True, help='Verbose')
@click.option('-c', '--config', help="Set config file")
@click.pass_context
def main(ctx, debug, verbose, config):  # pylint: disable=E1102
    """
    Main cli function
    """
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['CONFIG'] = config if config else DEFAULT_CONFIG_PATH
    if debug:
        print("hello")


@click.command()
@click.option('--list-tests', help="List tests")
@click.pass_context
def query(ctx, list_tests):
    """
    Query subcommand function
    """
    verbose = ctx.obj['VERBOSE']
    config = ctx.obj['CONFIG']
    if verbose:
        print("Hello World Query Verbose: {}".format(verbose))
    if config:
        print("Query: Using config file: {}".format(config))
    print("List tests: {}".format(list_tests))


@click.command()
@click.pass_context
def update_db(ctx):
    """
    Update-db subcommand function
    """
    verbose = ctx.obj['VERBOSE']
    config = ctx.obj['CONFIG']
    if verbose:
        click.echo("Hello This is verbose level: {}".format(verbose))
    print("Update-db: Using config file: {}".format(config))


main.add_command(query)
main.add_command(update_db)

if __name__ == "__main__":
    main()
