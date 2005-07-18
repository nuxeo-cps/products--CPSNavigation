# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""
CPSNavigation Installer

Howto use the CPSNavigation installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpsnavigation_install (or whatever)
     title         : CPSNavigation Install (or whatever)
     Module Name   : CPSNavigation.install
     Function Name : install

 - save it
 - then click on the test tab of this external method
"""

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from zLOG import LOG, INFO, DEBUG

class CPSNavigationInstaller(CPSInstaller):

    SKINS = {'cpsnavigation_default': 'Products/CPSNavigation/skins/cpsnavigation_default',
             'cpsnavigation_devel': 'Products/CPSNavigation/skins/cpsnavigation_devel',
             'cpsnavigation_images': 'Products/CPSNavigation/skins/cpsnavigation_images',
             }


    def verifyCatalogNavigationIndexes(self):
        indexes = (('container_path', 'FieldIndex', None),
                   ('relative_path_depth', 'FieldIndex', None),
                   ('relative_path', 'FieldIndex', None),
                   )
        metadata = ('relative_path',)

        # check indexes
        for index_name, index_type, index_extra in indexes:
            self.addPortalCatalogIndex(index_name, index_type, index_extra)
        # check metadata
        for name in metadata:
            self.addPortalCatalogMetadata(name)

    def install(self):
        self.log("Starting CPSNavigation install")
        self.verifySkins(self.SKINS)
        self.resetSkinCache()
        self.verifyWidgets(self.portal.getCPSNavigationWidgets())
        self.verifySchemas(self.portal.getCPSNavigationSchemas())
        self.verifyLayouts(self.portal.getCPSNavigationLayouts())
        self.verifyVocabularies(self.portal.getCPSNavigationVocabularies())
        self.setupTranslations()
        self.verifyCatalogNavigationIndexes()
        self.finalize()
        self.log("End of specific CPSNavigation install")

def install(self):
    installer = CPSNavigationInstaller(self, 'CPSNavigation')
    installer.install()
    return installer.logResult()
