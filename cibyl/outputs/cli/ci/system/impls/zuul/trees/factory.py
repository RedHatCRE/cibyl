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
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from anytree import find, PreOrderIter, findall
from overrides import overrides

from cibyl.models.ci.zuul.job import Job
from cibyl.outputs.cli.ci.system.impls.zuul.trees import Tree, Leaf

LOG = logging.getLogger(__name__)


class TreeFactory(ABC):
    @abstractmethod
    def from_jobs(self, jobs: Iterable[Job]) -> Tree:
        raise NotImplementedError


class FlatTreeFactory(TreeFactory):
    @overrides
    def from_jobs(self, jobs: Iterable[Job]) -> Tree:
        return Tree(
            name='.',
            children=[
                self._new_leaf_for(job)
                for job in jobs
            ]
        )

    def _new_leaf_for(self, job: Job) -> Leaf:
        return Leaf(name=job.name.value, model=job)


class HierarchicalTreeFactory(FlatTreeFactory):
    @overrides
    def from_jobs(self, jobs: Iterable[Job]) -> Tree:
        tree = super().from_jobs(jobs)

        for job in jobs:
            nodes = list(
                findall(tree, lambda leaf: leaf.name == job.name.value)
            )

            for variant in job.variants:
                parent = self._find_parent(tree, variant)

                if nodes:
                    node = nodes.pop()
                    node.parent = parent
                else:
                    parent.children = [
                        self._new_leaf_for(job),
                        *parent.children
                    ]

        return tree

    def _find_parent(self, tree: Tree, variant: Job.Variant) -> Leaf:
        if not variant.parent:
            return tree.root

        parent = find(tree, lambda leaf: leaf.name == variant.parent.value)

        if not parent:
            LOG.warning(
                "Parent for job: '%(job)s' not found on query results. "
                "Leaving job at root level...",
                {'job': variant.name.value}
            )
            return tree.root

        return parent
