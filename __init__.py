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

registerDirectory('skins', globals())

from ZODBNavigation import ZODBNavigation
allow_class(ZODBNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ZODBNavigation')

from ConfNavigation import ConfNavigation
allow_class(ConfNavigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ConfNavigation')


