# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
import os
from Testing.ZopeTestCase import ZopeLite
import Products
from Interface.Verify import verifyClass
from Products.CPSDefault.tests.ConfFinder import DummyClass as DC
from Products.CPSDefault.Navigation import Navigation
from ConfFinder import ConfFinder
from StringIO import StringIO


class TestNavigation(unittest.TestCase):

    def setUp(self):
        # setup a tree like this
        # root/
        # |-- leaf_1
        # |-- node_1
        # |   |-- leaf_2
        # |   `-- node_3
        # |       |-- leaf_4
        # |       |-- leaf_5
        # |       `-- node_4
        # `-- node_2
        #     `-- leaf_3
        text_conf="""
[root]
contents=node_1|node_2|leaf_1
[node_1]
contents=node_3|leaf_2
[node_2]
contents=leaf_3
[node_3]
contents=leaf_4|leaf_5|node_4
[node_4]
contents=
        """
        fd = StringIO(text_conf)
        self.finder = ConfFinder(file_fd=fd)

    def test_tree_01(self):
        current = DC('root')
        nav = Navigation(self.finder, current=current)
        tree = nav.getTree()
        self.assertEqual(tree[0]['object'], current)

    def test_tree_02(self):
        current = DC('node_1')
        nav = Navigation(self.finder, current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 4, nav.strTree(tree))
        self.assertEqual(tree[3]['id'], 'node_2', nav.strTree(tree))

    def test_tree_03(self):
        current = DC('root')
        nav = Navigation(self.finder, current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 3, nav.strTree(tree))
        self.assertEqual(tree[2]['id'], 'node_2', nav.strTree(tree))

    def test_tree_04(self):
        current = DC('node_3')
        nav = Navigation(self.finder, current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 5, nav.strTree(tree))
        self.assertEqual(tree[3]['id'], 'node_4', nav.strTree(tree))

    def test_tree_10(self):
        filename = os.path.join(Products.CPSDefault.__path__[0],
                                'tests', 'finder.data')
        finder = ConfFinder(filename=filename)
#        current = DC('mci/sections/domaines/informatique')
        current = DC('mci/sections/domaines/archives/recherche')
        nav = Navigation(finder, current=current)
        tree = nav.getTree()
        self.assertEqual(tree[4]['is_open'], 1, nav.strTree(tree,
                                                            show_obj=0))

    def test_list_01(self):
        current = DC('root')
        nav = Navigation(self.finder, current=current)
        items = nav.getListing()
        self.assertEqual(items, [DC('node_1'), DC('node_2'), DC('leaf_1')],
                         items)


def test_suite():
    return unittest.makeSuite(TestNavigation)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
