# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite, ZopeTestCase, installProduct, app


from Interface.Verify import verifyClass
from Products.CPSNavigation.interfaces.IFinder import IFinder
from Products.CPSNavigation.LDAPDirectoryNavigation import LDAPDirectoryNavigation

class TestLDAPDirectoryFinder(ZopeTestCase):

    def test_interface(self):
        verifyClass(IFinder, LDAPDirectoryNavigation)



def test_suite():
    return unittest.makeSuite(TestLDAPDirectoryFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
