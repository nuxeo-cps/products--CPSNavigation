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

from Navigation import Navigation
allow_class(Navigation)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('Navigation')

from ZODBFinder import ZODBFinder
allow_class(ZODBFinder)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ZODBFinder')

from ConfFinder import ConfFinder
allow_class(ConfFinder)
ModuleSecurityInfo('Products.CPSNavigation').declarePublic('ConfFinder')
