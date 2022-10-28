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
from anytree import AsciiStyle, RenderTree

from cibyl.models.ci.zuul.job import Job
from cibyl.outputs.cli.printer import ColoredPrinter
from kernel.tools.text import IndentedTextBuilder
from kernel.tools.tree import Tree


class HierarchyCascade(ColoredPrinter):
    """Section of a Zuul source output that takes care of printing the
    relationship existing between its elements.
    """

    def print_tree(self, tree: Tree[Job]) -> str:
        """Textual representation of the parent-child relationship between
        Zuul jobs as indicated by the hierarchical tree given as input.

        Output example::
            .
            +-- base
                +-- example-job

        :param tree: Structure indicating the relationship between jobs.
        :return: ASCII-style text portrayal of the tree.
        """
        result = IndentedTextBuilder()
        renderer = RenderTree(node=tree.root, style=AsciiStyle())

        result.add(renderer.by_attr(attrname='name'), 0)

        return result.build()
