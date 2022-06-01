"""
# Copyright 2022 Red Hat
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
# pylint: disable=no-member
import unittest

from cibyl.models.attribute import (AttributeDictValue, AttributeListValue,
                                    AttributeValue)


class TestAttributeValue(unittest.TestCase):
    """Testing AttributeValue model"""

    def setUp(self):
        self.name = "test"
        self.value = "test_value"
        self.attr = AttributeValue(self.name, attr_type=str,
                                   value=self.value)

    def test_init(self):
        """Test __init__ method of AttributeValue."""
        self.assertEqual(self.name, self.attr.name)
        self.assertEqual(self.value, self.attr.value)
        self.assertEqual(str, self.attr.attr_type)
        self.assertIsNone(self.attr.arguments)

    def test_eq(self):
        """Test __eq__ method of AttributeValue."""
        attr2 = AttributeValue(self.name, attr_type=str,
                               value="test_value")
        self.assertEqual(self.attr, attr2)
        attr2 = AttributeValue("name", attr_type=str,
                               value="test_value")
        self.assertNotEqual(self.attr, attr2)
        attr2 = AttributeValue(self.name, attr_type=str,
                               value="value")
        self.assertNotEqual(self.attr, attr2)

    def test_str(self):
        """Test __str__ method of AttributeValue."""
        self.assertEqual(str(self.attr), self.value)


class TestAttributeListValue(unittest.TestCase):
    """Test AttributeListValue model"""

    def setUp(self):
        self.name = "test"
        self.value = ["test_value"]
        self.attr = AttributeListValue(self.name, attr_type=str,
                                       value=self.value)

    def test_init(self):
        """Test __init__ method of AttributeListValue."""
        self.assertEqual(self.name, self.attr.name)
        self.assertEqual(self.value, self.attr.value)
        self.assertEqual(str, self.attr.attr_type)
        self.assertIsNone(self.attr.arguments)

    def test_init_non_list_value(self):
        """Test __init__ method of AttributeListValue with a value not of
        type list."""
        attr2 = AttributeListValue(self.name, attr_type=str,
                                   value="test_value")
        self.assertEqual(self.name, attr2.name)
        self.assertEqual("test_value", attr2.value)
        self.assertEqual(str, attr2.attr_type)
        self.assertIsNone(attr2.arguments)

    def test_init_none_value(self):
        """Test __init__ method of AttributeListValue with a value of
        type None."""
        attr2 = AttributeListValue(self.name, attr_type=str,
                                   value=None)
        self.assertEqual(self.name, attr2.name)
        self.assertEqual([], attr2.value)
        self.assertEqual(str, attr2.attr_type)
        self.assertIsNone(attr2.arguments)

    def test_eq(self):
        """Test __eq__ method of AttributeListValue."""
        attr2 = AttributeListValue(self.name, attr_type=str,
                                   value=self.value)
        self.assertEqual(self.attr, attr2)
        attr2 = AttributeListValue("name", attr_type=str,
                                   value="test_value")
        self.assertNotEqual(self.attr, attr2)
        attr2 = AttributeListValue(self.name, attr_type=str,
                                   value="value")
        self.assertNotEqual(self.attr, attr2)

    def test_str(self):
        """Test __str__ method of AttributeListValue."""
        self.assertEqual(str(self.attr), str(self.value))

    def test_get_item(self):
        """Test __getitem__ method of type AttributeListValue."""
        self.assertEqual(self.attr[0], self.value[0])
        self.assertEqual(self.attr[-1], self.value[-1])
        with self.assertRaises(IndexError):
            print(self.attr[3])

    def test_len(self):
        """Test __len__ method of type AttributeListValue."""
        self.assertEqual(len(self.attr), 1)

    def test_append(self):
        """Test append method of type AttributeListValue."""
        self.assertEqual(len(self.attr), 1)
        self.attr.append("second")
        self.assertEqual(len(self.attr), 2)


class TestAttributeDictValue(unittest.TestCase):
    """Test AttributeDictValue model"""

    def setUp(self):
        self.name = "test"
        self.value = {"test_value": "value"}
        self.attr = AttributeDictValue(self.name, attr_type=str,
                                       value=self.value)

    def test_init(self):
        """Test __init__ method of AttributeDictValue."""
        self.assertEqual(self.name, self.attr.name)
        self.assertEqual(self.value, self.attr.value)
        self.assertEqual(str, self.attr.attr_type)
        self.assertIsNone(self.attr.arguments)

    def test_init_non_dict_value(self):
        """Test __init__ method of AttributeDictValue with a value not of
        type dict."""
        attr2 = AttributeDictValue(self.name, attr_type=str,
                                   value="test_value")
        self.assertEqual(self.name, attr2.name)
        self.assertEqual("test_value", attr2.value)
        self.assertEqual(str, attr2.attr_type)
        self.assertIsNone(attr2.arguments)

    def test_init_none_value(self):
        """Test __init__ method of AttributeDictValue with a value of
        type None."""
        attr2 = AttributeDictValue(self.name, attr_type=str,
                                   value=None)
        self.assertEqual(self.name, attr2.name)
        self.assertEqual({}, attr2.value)
        self.assertEqual(str, attr2.attr_type)
        self.assertIsNone(attr2.arguments)

    def test_eq(self):
        """Test __eq__ method of AttributeDictValue."""
        attr2 = AttributeDictValue(self.name, attr_type=str,
                                   value=self.value)
        self.assertEqual(self.attr, attr2)
        attr2 = AttributeDictValue("name", attr_type=str,
                                   value="test_value")
        self.assertNotEqual(self.attr, attr2)
        attr2 = AttributeDictValue(self.name, attr_type=str,
                                   value="value")
        self.assertNotEqual(self.attr, attr2)

    def test_str(self):
        """Test __str__ method of AttributeDictValue."""
        self.assertEqual(str(self.attr), str(self.value))

    def test_get_item(self):
        """Test __getitem__ method of type AttributeDictValue."""
        self.assertEqual(self.attr["test_value"], self.value["test_value"])
        with self.assertRaises(KeyError):
            print(self.attr["3"])

    def test_set_item(self):
        """Test __setitem__ method of type AttributeDictValue."""
        self.attr["key"] = "value"
        self.assertEqual(self.attr["key"], "value")

    def test_len(self):
        """Test __len__ method of type AttributeDictValue."""
        self.assertEqual(len(self.attr), 1)

    def test_iter(self):
        """Test __iter__ method of type AttributeDictValue."""
        keys = list(self.attr)
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0], "test_value")

    def test_delitem(self):
        """Test __delitem__ method of type AttributeDictValue."""
        del self.attr["test_value"]
        self.assertEqual(len(self.attr), 0)

    def test_items(self):
        """Test items method of type AttributeDictValue."""
        items = self.attr.items()
        self.assertEqual(len(items), 1)
        self.assertIn(('test_value', 'value'), items)

    def test_values(self):
        """Test values method of type AttributeDictValue."""
        values = self.attr.values()
        self.assertEqual(len(values), 1)
        self.assertIn('value', values)

    def test_keys(self):
        """Test keys method of type AttributeDictValue."""
        keys = self.attr.keys()
        self.assertEqual(len(keys), 1)
        self.assertIn('test_value', keys)

    def test_get(self):
        """Test get method of type AttributeDictValue."""
        self.assertEqual(self.attr.get("test_value"), "value")
        self.assertEqual(self.attr.get("missing", "default"), "default")
        self.assertIsNone(self.attr.get("missing"))
