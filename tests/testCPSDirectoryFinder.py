# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite, ZopeTestCase, installProduct, app


from Interface.Verify import verifyClass
from Products.CPSNavigation.interfaces.IFinder import IFinder
from Products.CPSNavigation.CPSDirectoryNavigation import CPSDirectoryNavigation

class TestCPSDirectoryFinder(ZopeTestCase):

    def test_interface(self):
        verifyClass(IFinder, CPSDirectoryNavigation)



def test_suite():
    return unittest.makeSuite(TestCPSDirectoryFinder)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
