# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
import os
from Testing.ZopeTestCase import ZopeLite
import Products
from Products.CPSNavigation.ConfNavigation import DummyClass as DC, \
     ConfNavigation

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
        file_content="""
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
        self.fc = file_content

    def test_tree_01(self):
        current = DC('root')
        nav = ConfNavigation(file_content=self.fc,
                         root_uid='root',
                         current=current)
        tree = nav.getTree()
        self.assertEqual(tree[0]['object'], current)

    def test_tree_02(self):
        current = DC('node_1')
        nav = ConfNavigation(file_content=self.fc,
                         root_uid='root',
                         current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 4, nav._strTree(tree))
        self.assertEqual(tree[3]['uid'], 'node_2', nav._strTree(tree))

    def test_tree_03(self):
        current = DC('root')
        nav = ConfNavigation(file_content=self.fc,
                             root_uid='root',
                             current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 3, nav._strTree(tree))
        self.assertEqual(tree[2]['uid'], 'node_2', nav._strTree(tree))

    def test_tree_04(self):
        current = DC('node_3')
        nav = ConfNavigation(file_content=self.fc,
                             root_uid='root',
                             current=current)
        tree = nav.getTree()
        self.assertEqual(len(tree), 5, nav._strTree(tree))
        self.assertEqual(tree[3]['uid'], 'node_4', nav._strTree(tree))


    def test_tree_05(self):
        nav = ConfNavigation(file_content=self.fc,
                             current_uid='leaf_3',
                             root_uid='root')
        tree = nav.getTree()
        self.assert_(tree[0]['uid'] == 'root', nav._strTree(tree))

    def test_tree_10(self):
        file_name = os.path.join(Products.CPSNavigation.__path__[0],
                                 'tests', 'finder.data')
        # current = DC('mci/sections/domaines/informatique')
        current = DC('mci/sections/domaines/archives/recherche')
        nav = ConfNavigation(file_name=file_name,
                             root_uid='root', current=current)
        tree = nav.getTree()
        self.assertEqual(tree[4]['is_open'], 1, nav._strTree(tree,
                                                            show_obj=0))

    def test_tree_20(self):
        nav = ConfNavigation(file_content=self.fc,
                             current_uid='leaf_3',
                             root_uid='root',
                             include_root=0)
        tree = nav.getTree()
        self.assert_(tree[0]['uid'] == 'node_1', nav._strTree(tree))

    
    def test_tree_21(self):
        nav = ConfNavigation(file_content="""[root]
        """,
                             current_uid='root',
                             root_uid='root',
                             include_root=0)
        tree = nav.getTree()
        self.assert_(len(tree) == 0, nav._strTree(tree))


    def test_tree_21(self):
        nav = ConfNavigation(file_content="""[root]
contents=node_1
[node_1]
contents=
        """,
                             current_uid='node_1',
                             root_uid='root',
                             include_root=0)
        tree = nav.getTree()
        self.assert_(len(tree) == 1, nav._strTree(tree))

    


    def test_listing_01(self):
        current = DC('root')
        nav = ConfNavigation(file_content=self.fc,
                         root_uid='root',
                         current=current)
        items, batch_info = nav.getListing()
        # items is a batched !
        self.assertEqual([items[0], items[1], items[2]],
                         [DC('node_1'), DC('node_2'), DC('leaf_1')],
                         items)


def test_suite():
    return unittest.makeSuite(TestNavigation)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
