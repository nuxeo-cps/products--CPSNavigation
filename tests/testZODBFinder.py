# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite, ZopeTestCase, installProduct, app


from Interface.Verify import verifyClass
from Products.CPSDefault.interfaces.Finder import Finder as IFinder
from Products.CPSDefault.CMFFinder import CMFFinder

installProduct('CMFCore', quiet=1)
installProduct('CMFDefault', quiet=1)
installProduct('MailHost', quiet=1)

class TestCMFFinder(ZopeTestCase):

    def afterSetUp(self):
        from Products.CMFDefault.Portal import manage_addCMFSite
        id='testsite'
        manage_addCMFSite(self.app, id)
        self.portal = self.app[id]
        self.finder = CMFFinder()
        self.finder.setParams(root=self.portal)

    def test_interface(self):
        verifyClass(IFinder, CMFFinder)

    def test_getObject_01(self):
        node = self.finder.getObject('testsite/Members')
        self.assertEqual(node, self.portal.Members, node)

    def test_getObject_02(self):
        node = self.finder.getObject('XXX')
        self.assertEqual(node, None, node)

    def test_getUid_01(self):
        uid_ = 'testsite/Members'
        node = self.finder.getObject(uid_)
        uid = self.finder.getUid(node)
        self.assertEqual(uid, uid_, uid)

    def test_isNode_01(self):
        self.assertEqual(self.finder.isNode(self.portal), 1)

    def test_isNode_02(self):
        self.assertEqual(self.finder.isNode(self.portal.portal_url), 0)

    def test_getChildren_01(self):
        self.assert_(self.portal.portal_url in \
                     self.finder.getChildren(self.portal))

    def test_hasChildren_01(self):
        self.assert_(self.finder.hasChildren(self.portal))

    def test_getParent_01(self):
        self.assertEqual(self.finder.getParent(self.portal.Members),
                         self.portal)



def test_suite():
    return unittest.makeSuite(TestCMFFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
