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
from typing import Any, Generic, Iterable, Optional, TypeVar

from anytree import NodeMixin, findall

T = TypeVar("T", bound=Any)
"""Generic type that can represent anything."""


class Leaf(Generic[T], NodeMixin):
    """Node for a :class:`Tree`.

    Each node on the tree has the chance of storing a value of type T within
    it. This allows the structure to be used like a multi-level dictionary, as
    each leaf has its own identifier too.

    This class acts as a wrapper over the 'anytree' library. For examples
    and deeper documentation, pleaser refer to:
    https://anytree.readthedocs.io/en/latest/
    """

    def __init__(
        self,
        name: str,
        parent: Optional['Leaf[T]'] = None,
        children: Optional[Iterable['Leaf[T]']] = None,
        value: Optional[T] = None
    ):
        """Constructor.

        :param name: Identifier for the node. These are not unique and can
            be shared by multiple nodes.
        :param parent: Node from which this one hangs below.
        :param children: Nodes that hang from this one.
        :param value: Additional data stored within the node.
        """
        super().__init__()

        if children is None:
            children = ()

        # Mixin values
        self.parent = parent
        self.children = children

        # Own values
        self.name = name
        self.value = value


class Tree(Generic[T]):
    """Implementation of a generic tree data structure. Each node of the
    tree is allowed to have as many children as desired.

    Unlike other implementations, this class is not a node itself,
    but instead a utility to perform tasks over the whole structure. One
    can access the root node for lower level actions.

    This class acts as a wrapper over the 'anytree' library. For examples
    and deeper documentation, pleaser refer to:
    https://anytree.readthedocs.io/en/latest/
    """

    def __init__(self, root: Leaf[T]):
        """Constructor.

        :param root: Higher-level node of the tree. Most probably, this one
            will be the one to not have any parent above. It is possible though
            to create a tree from a lower-level node that ignored everything
            above it.
        """
        self._root = root

    @property
    def root(self) -> Leaf[T]:
        """
        :return: Node considered to be the start of the tree.
        """
        return self._root

    def find_by_name(self, name: str) -> Iterable[Leaf[T]]:
        """Looks for all nodes on the tree that have the given identifier.

        :param name: The identifier to look for.
        :return: List of all leaves that match the condition.
        """
        return findall(self.root, lambda leaf: leaf.name == name)
