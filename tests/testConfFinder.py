# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Interface.Verify import verifyClass
from Products.CPSNavigation.ConfNavigation import ConfNavigation, \
     DummyClass as DC
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
        self.nav = ConfNavigation(root_uid='root',
                                  current_uid='root',
                                  file_content=file_content)

    def test_interface(self):
        verifyClass(IFinder, ConfNavigation)

    def test_getObject_01(self):
        node_ = DC('node_2')
        node = self.nav._getObject('node_2')
        self.assertEqual(node, node_, node)

    def test_getObject_03(self):
        # XXX ConfNav getObject always return even if uid is unknown
        node_ = DC('XXX')
        node = self.nav._getObject('XXX')
        self.assertEqual(node, node_, node)

    def test_getUid_01(self):
        uid_ = 'node_3'
        node = self.nav._getObject(uid_)
        uid = self.nav._getUid(node)
        self.assertEqual(uid, uid_, uid)

    def test_isNode_01(self):
        self.assertEqual(self.nav._isNode(DC('root')), 1)

    def test_isNode_02(self):
        self.assertEqual(self.nav._isNode(DC('node_2')), 1)

    def test_isNode_03(self):
        self.assertEqual(self.nav._isNode(DC('leaf_1')), 0)

    def test_isNode_04(self):
        self.assertEqual(self.nav._isNode(DC('leaf_3')), 0)

    def test_getParent_01(self):
        current = DC('node_1')
        parent = self.nav._getParent(current)
        self.assertEqual(parent, DC('root'), parent)

    def test_getParent_02(self):
        current = DC('leaf_4')
        parent = self.nav._getParent(current)
        self.assertEqual(parent, DC('node_3'), parent)

    def test_getParent_03(self):
        current = DC('root')
        parent = self.nav._getParent(current)
        self.assertEqual(parent, None, parent)

    def test_getParent_04(self):
        current = DC('leaf_1')
        parent = self.nav._getParent(current)
        self.assertEqual(parent, DC('root'), parent)

    def test_getParent_05(self):
        current = DC('foo')
        try:
            parent = self.nav._getParent(current)
        except KeyError:
            pass
        else:
            self.assert_(0, 'expecting KeyError exception')

    def test_getParent_06(self):
        current = DC('leaf_3')
        parent = self.nav._getParent(current)
        self.assertEqual(parent, DC('node_2'), parent)
    

    def test_getChildren_01(self):
        self.assertEqual(self.nav._getChildren(DC('root')),
                         [DC('node_1'),
                          DC('node_2'),
                          DC('leaf_1')])

    def test_getChildren_02(self):
        self.assertEqual(self.nav._getChildren(DC('node_3')),
                         [DC('leaf_4'), DC('leaf_5')])

    def test_getChildren_03(self):
        self.assertEqual(self.nav._getChildren(DC('leaf_1')), [])

    def test_getChildren_04(self):
        # XXX ConfNavigation should raise KeyError for invalid key
        self.assertEqual(self.nav._getChildren(DC('foo')), [])

    def test_getChildren_05(self):
        self.assertEqual(self.nav._getChildren(DC('root'),
                                                 no_nodes=1),
                         [DC('leaf_1')])

    def test_getChildren_06(self):
        self.assertEqual(self.nav._getChildren(DC('root'),
                                                 no_leaves=1),
                         [DC('node_1'), DC('node_2')])




def test_suite():
    return unittest.makeSuite(TestConfFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
