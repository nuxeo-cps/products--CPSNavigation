# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Interface.Verify import verifyClass
from Products.CPSNavigation.ConfFinder import ConfFinder, DummyClass as DC
from Products.CPSNavigation.interfaces.IFinder import IFinder


class TestConfFinder(unittest.TestCase):
    def setUp(self):
        # setup a tree like this
        # root/
        # |-- leaf_1
        # |-- node_1
        # |   |-- leaf_2
        # |   `-- node_3
        # |       |-- leaf_4
        # |       `-- leaf_5
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
contents=leaf_4|leaf_5
        """
        self.finder = ConfFinder(file_content=file_content)
        self.finder.setParams(root=DC('root'))

    def test_interface(self):
        verifyClass(IFinder, ConfFinder)

    def test_getObject_01(self):
        node_ = DC('node_2')
        node = self.finder.getObject('node_2')
        self.assertEqual(node, node_, node)

    def test_getObject_03(self):
        node_ = None
        node = self.finder.getObject('XXX')
        self.assertEqual(node, node_, node)

    def test_getUid_01(self):
        uid_ = 'node_3'
        node = self.finder.getObject(uid_)
        uid = self.finder.getUid(node)
        self.assertEqual(uid, uid_, uid)

    def test_isNode_01(self):
        self.assertEqual(self.finder.isNode(DC('root')), 1)

    def test_isNode_02(self):
        self.assertEqual(self.finder.isNode(DC('node_2')), 1)

    def test_isNode_03(self):
        self.assertEqual(self.finder.isNode(DC('leaf_1')), 0)

    def test_isNode_04(self):
        self.assertEqual(self.finder.isNode(DC('leaf_3')), 0)

    def test_getParent_01(self):
        current = DC('node_1')
        parent = self.finder.getParent(current)
        self.assertEqual(parent, DC('root'), parent)

    def test_getParent_02(self):
        current = DC('leaf_4')
        parent = self.finder.getParent(current)
        self.assertEqual(parent, DC('node_3'), parent)

    def test_getParent_03(self):
        current = DC('root')
        parent = self.finder.getParent(current)
        self.assertEqual(parent, None, parent)

    def test_getParent_04(self):
        current = DC('leaf_1')
        parent = self.finder.getParent(current)
        self.assertEqual(parent, DC('root'), parent)

    def test_getParent_05(self):
        current = DC('foo')
        try:
            parent = self.finder.getParent(current)
        except KeyError:
            pass
        else:
            self.assert_(0, 'expecting KeyError exception')

    def test_getChildren_01(self):
        self.assertEqual(self.finder.getChildren(DC('root')),
                         [DC('node_1'),
                          DC('node_2'),
                          DC('leaf_1')])

    def test_getChildren_02(self):
        self.assertEqual(self.finder.getChildren(DC('node_3')),
                         [DC('leaf_4'), DC('leaf_5')])

    def test_getChildren_03(self):
        self.assertEqual(self.finder.getChildren(DC('leaf_1')), [])

    def test_getChildren_04(self):
        # XXX ConfFinder should raise KeyError for invalid key
        self.assertEqual(self.finder.getChildren(DC('foo')), [])

    def test_getChildren_05(self):
        self.assertEqual(self.finder.getChildren(DC('root'),
                                                 no_nodes=1),
                         [DC('leaf_1')])

    def test_getChildren_06(self):
        self.assertEqual(self.finder.getChildren(DC('root'),
                                                 no_leaves=1),
                         [DC('node_1'), DC('node_2')])




def test_suite():
    return unittest.makeSuite(TestConfFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
