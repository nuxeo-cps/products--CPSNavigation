# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite, installProduct, app


from Interface.Verify import verifyClass
from Products.CPSDefault.interfaces.Finder import Finder as IFinder
from Products.CPSDefault.CMFFinder import CMFFinder

installProduct('CMFCore', quiet=1)
installProduct('CMFDefault', quiet=1)
installProduct('MailHost', quiet=1)

class TestCMFFinder(unittest.TestCase):

    def setUp(self):
        self.app = app()
        from Products.CMFDefault.Portal import manage_addCMFSite
        id='testsite'
        manage_addCMFSite(self.app, id)
        self.portal = self.app[id]
        self.finder = CMFFinder()

    def test_interface(self):
        verifyClass(IFinder, CMFFinder)

    def test_isNode_01(self):
        self.assertEqual(self.finder.isNode(self.portal), 1)

    def test_isNode_02(self):
        self.assertEqual(self.finder.isNode(self.portal.portal_url), 0)

    def test_getChildren_01(self):
        self.assert_(self.portal.portal_url in \
                     self.finder.getChildren(self.portal))

    def test_getParents_01(self):
        self.assertEqual(self.finder.getParents(self.portal.Members)[0],
                         self.portal)


def test_suite():
    return unittest.makeSuite(TestCMFFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
