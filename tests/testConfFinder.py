# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Interface.Verify import verifyClass
from Products.CPSDefault.tests.ConfFinder import ConfFinder, DummyClass as DC
from Products.CPSDefault.interfaces.Finder import Finder as IFinder
from StringIO import StringIO


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
        text_conf="""
[root]
contents=node_1|node_2|leaf_1
[node_1]
contents=node_3|leaf_2
[node_2]
contents=leaf_3
[node_3]
contents=leaf_4|leaf_5
        """
        fd = StringIO(text_conf)
        self.finder = ConfFinder(file_fd=fd)

    def test_interface(self):
        verifyClass(IFinder, ConfFinder)

    def test_isNode_01(self):
        self.assertEqual(self.finder.isNode(DC('root')), 1)

    def test_isNode_02(self):
        self.assertEqual(self.finder.isNode(DC('node_2')), 1)

    def test_isNode_03(self):
        self.assertEqual(self.finder.isNode(DC('leaf_1')), 0)

    def test_isNode_04(self):
        self.assertEqual(self.finder.isNode(DC('leaf_3')), 0)

    def test_getParents_01(self):
        _children = []
        child = DC('root')
        while 1:
            r = self.finder.getChildren(child)
            if not r:
                break
            _children.append(child)
            child = r[0]

        _children.reverse()
        children = self.finder.getParents(child)
        self.assertEqual(children, _children)

    def test_getParents_02(self):
        current = DC('leaf_4')
        parents = self.finder.getParents(current)
        self.assertEqual(parents, [DC('node_3'),
                                   DC('node_1'),
                                   DC('root')], parents)

    def test_getParents_03(self):
        current = DC('root')
        parents = self.finder.getParents(current)
        self.assertEqual(parents, [], parents)

    def test_getParents_04(self):
        current = DC('leaf_1')
        parents = self.finder.getParents(current)
        self.assertEqual(parents, [DC('root')], parents)

    def test_getParents_05(self):
        current = DC('node_1')
        parents = self.finder.getParents(current)
        self.assertEqual(parents, [DC('root')], parents)

    def test_getParents_06(self):
        current = DC('foo')
        try:
            parents = self.finder.getParents(current)
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
