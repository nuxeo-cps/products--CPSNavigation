# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite, ZopeTestCase, installProduct, app


from Interface.Verify import verifyClass
from Products.CPSNavigation.interfaces.IFinder import IFinder
from Products.CPSNavigation.ZODBNavigation import ZODBNavigation

installProduct('CMFCore', quiet=1)
installProduct('CMFDefault', quiet=1)
installProduct('MailHost', quiet=1)

class TestZODBFinder(ZopeTestCase):

    def afterSetUp(self):
        from Products.CMFDefault.Portal import manage_addCMFSite
        id='testsite'
        manage_addCMFSite(self.app, id)
        self.portal = self.app[id]
        self.nav = ZODBNavigation(root=self.portal,
                                  current=self.portal)

    def test_interface(self):
        verifyClass(IFinder, ZODBNavigation)

    def test_getObject_01(self):
        node = self.nav._getObject('testsite/Members')
        self.assertEqual(node, self.portal.Members, node)

    def test_getObject_02(self):
        node = self.nav._getObject('XXX')
        self.assertEqual(node, None, node)

    def test_getUid_01(self):
        uid_ = 'testsite/Members'
        node = self.nav._getObject(uid_)
        uid = self.nav._getUid(node)
        self.assertEqual(uid, uid_, uid)

    def test_isNode_01(self):
        self.assertEqual(self.nav._isNode(self.portal), 1)

    def test_isNode_02(self):
        self.assertEqual(self.nav._isNode(self.portal.portal_url), 0)

    def test_getChildren_01(self):
        self.assert_(self.portal.portal_url in \
                     self.nav._getChildren(self.portal))

    def test_hasChildren_01(self):
        self.assert_(self.nav._hasChildren(self.portal))

    def test_getParentUid_01(self):
        current_uid = self.nav._getUid(self.portal.Members)
        parent_uid = self.nav._getParentUid(current_uid)
        self.assertEqual(parent_uid, 'testsite', parent_uid)



def test_suite():
    return unittest.makeSuite(TestZODBFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
