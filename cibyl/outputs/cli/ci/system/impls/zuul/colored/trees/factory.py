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
from typing import Iterable

from overrides import overrides

from cibyl.models.ci.zuul.job import Job
from cibyl.utils.tree import Leaf, Tree

LOG = logging.getLogger(__name__)


class TreeFactory(ABC):
    @abstractmethod
    def from_jobs(self, jobs: Iterable[Job]) -> Tree[Job]:
        raise NotImplementedError


class FlatTreeFactory(TreeFactory):
    ROOT_NAME: str = '.'

    @overrides
    def from_jobs(self, jobs: Iterable[Job]) -> Tree[Job]:
        return Tree(
            root=Leaf[Job](
                name=self.ROOT_NAME,
                children=[self._new_detached_leaf(job) for job in jobs],
                value=None
            )
        )

    def _new_detached_leaf(self, job: Job) -> Leaf[Job]:
        return Leaf(name=job.name.value, value=job)


class HierarchicalTreeFactory(FlatTreeFactory):
    @overrides
    def from_jobs(self, jobs: Iterable[Job]) -> Tree[Job]:
        # First iteration -> List all jobs without a hierarchy.
        # This will avoid conflicts when a child is added before its parent.
        tree = super().from_jobs(jobs)

        # Second iteration -> Generate the hierarchy.
        for job in jobs:
            # Look for the leaves of the job, just one at the start.
            leaves = list(tree.find_by_name(job.name.value))

            for variant in job.variants.value:
                # Look for the leaf to fall under
                parent = self._find_parent(tree, variant)

                if leaves:
                    # If we already have leaves for the job, use those
                    leaf = leaves.pop()
                    leaf.parent = parent
                else:
                    # Otherwise, add a new one
                    parent.children = [
                        self._new_detached_leaf(job),
                        *parent.children
                    ]

        return tree

    def _find_parent(self, tree: Tree[Job], variant: Job.Variant) -> Leaf[Job]:
        if not variant.parent:
            LOG.debug(
                "Found root job at: '%(job)s'.",
                {'job': variant.name.value}
            )
            return tree.root

        parents = list(tree.find_by_name(variant.parent.value))

        if not parents:
            LOG.warning(
                "Parent for job: '%(job)s' not found on query results. "
                "Leaving job at root level...",
                {'job': variant.name.value}
            )
            return tree.root

        if len(parents) > 1:
            # TODO: Figure out what to link to on these cases
            LOG.warning(
                "More than one parent for job: '%(job)s' found on query "
                "results. Leaving job at root level...",
                {'job': variant.name.value}
            )
            return tree.root

        return parents[0]
