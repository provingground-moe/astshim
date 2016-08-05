from __future__ import absolute_import, division, print_function
import unittest

import astshim
from astshim.test import ObjectTestCase


class TestObject(ObjectTestCase):

    def test_attributes(self):
        """Test accessing object attributes
        """
        nin = 2
        zoom = 1.3
        obj = astshim.ZoomMap(nin, zoom)

        self.assertEqual(obj.getClass(), "ZoomMap")

        self.assertTrue(obj.hasAttribute("ID"))
        self.assertTrue(obj.hasAttribute("Ident"))
        self.assertTrue(obj.hasAttribute("UseDefs"))

        self.assertEqual(obj.getID(), "")
        self.assertEqual(obj.getIdent(), "")
        self.assertEqual(obj.getUseDefs(), True)

    def test_unknown_attributes(self):
        """Test accessing unknown attributes"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertFalse(obj.hasAttribute("NonExistentAttribute"))

        with self.assertRaises(Exception):
            obj.getC("NonExistentAttribute")
        with self.assertRaises(Exception):
            obj.getF("NonExistentAttribute")
        with self.assertRaises(Exception):
            obj.getD("NonExistentAttribute")
        with self.assertRaises(Exception):
            obj.getI("NonExistentAttribute")
        with self.assertRaises(Exception):
            obj.getL("NonExistentAttribute")

    def test_clear_and_test(self):
        """Test Object.clear and Object.test"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertFalse(obj.test("ID"))
        obj.setID("initial_id")
        self.assertEqual(obj.getID(), "initial_id")
        self.assertTrue(obj.test("ID"))
        obj.clear("ID")
        self.assertEqual(obj.getID(), "")
        self.assertFalse(obj.test("ID"))

    def test_copy_and_same(self):
        """Test Object.copy and Object.same"""
        obj = astshim.ZoomMap(2, 1.3, "Ident=original")

        # there may be more than one object in existence if run with pytest
        initialNumObj = obj.getNobject()

        self.checkCopy(obj)
        cp = obj.copy()
        # a deep copy does not increment
        self.assertEqual(obj.getRefCount(), 1)

        seriesMap = obj.of(obj)
        # obj itself plus two copies in the SeriesMap
        self.assertEqual(obj.getRefCount(), 3)
        del seriesMap
        self.assertEqual(obj.getRefCount(), 1)

        cp.setIdent("copy")
        self.assertEqual(cp.getIdent(), "copy")
        self.assertEqual(obj.getIdent(), "original")

        del cp
        self.assertEqual(obj.getNobject(), initialNumObj)
        self.assertEqual(obj.getRefCount(), 1)

    def test_id(self):
        """Test that ID is *not* transferred to copies"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertEqual(obj.getID(), "")
        obj.setID("initial_id")
        self.assertEqual(obj.getID(), "initial_id")
        cp = obj.copy()
        self.assertEqual(cp.getID(), "")

    def test_ident(self):
        """Test that Ident *is* transferred to copies"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertEqual(obj.getIdent(), "")
        obj.setIdent("initial_ident")
        self.assertEqual(obj.getIdent(), "initial_ident")
        cp = obj.copy()
        self.assertEqual(cp.getIdent(), "initial_ident")


if __name__ == "__main__":
    unittest.main()
