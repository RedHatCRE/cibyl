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
from unittest import TestCase
from unittest.mock import Mock

from kernel.tools.tree import Leaf, Tree


class TestLeaf(TestCase):
    """Test for :class:`Leaf`.
    """

    def test_name(self):
        """Checks that the name of the leaf is stored.
        """
        name = 'test'

        leaf = Leaf[str](name=name, value=None)

        self.assertEqual(name, leaf.name)

    def test_value(self):
        """Checks that the value stored by the leaf is settable.
        """
        name = 'test'
        value = 'val1'

        leaf = Leaf[str](name=name, value=value)

        self.assertEqual(value, leaf.value)

        other_value = 'val2'

        leaf.value = other_value

        self.assertEqual(other_value, leaf.value)


class TestTree(TestCase):
    """Tests for :class:`Tree`.
    """

    def test_root(self):
        """Checks that the tree is rooted in the given leaf.
        """
        leaf = Mock()

        tree = Tree[str](root=leaf)

        self.assertEqual(leaf, tree.root)

    def test_find_by_name(self):
        """Checks that the tree is capable of filtering its leaves by name.
        """
        leaf1 = Mock()
        leaf1.name = '1'
        leaf1.children = ()

        leaf2 = Mock()
        leaf2.name = '1'
        leaf2.children = ()

        leaf3 = Mock()
        leaf3.name = '3'
        leaf3.children = ()

        root = Mock()
        root.name = '.'
        root.children = [leaf1, leaf2, leaf3]

        tree = Tree[str](root=root)

        self.assertEqual(
            (
                leaf1,
                leaf2
            ),
            tree.find_by_name(name='1')
        )
