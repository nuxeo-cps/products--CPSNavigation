# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
""" CPS Default Init
"""
from AccessControl import ModuleSecurityInfo
from Products.PythonScripts.Utility import allow_class
from Products.CMFCore.DirectoryView import registerDirectory

import CatalogNavigationWidget

registerDirectory('skins', globals())

from ConfNavigation import ConfNavigation
allow_class(ConfNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ConfNavigation')

from ZODBNavigation import ZODBNavigation
allow_class(ZODBNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ZODBNavigation')

from CPSNavigation import CPSNavigation
allow_class(CPSNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('CPSNavigation')

from CatalogNavigation import CatalogNavigation
allow_class(CatalogNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('CatalogNavigation')

from LDAPDirectoryNavigation import LDAPDirectoryNavigation
allow_class(LDAPDirectoryNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic(
    'LDAPDirectoryNavigation')

from CPSDirectoryNavigation import CPSDirectoryNavigation
allow_class(CPSDirectoryNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic(
    'CPSDirectoryNavigation')

from CPSIndirectDirectoryNavigation import CPSIndirectDirectoryNavigation
allow_class(CPSIndirectDirectoryNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic(
    'CPSIndirectDirectoryNavigation')
