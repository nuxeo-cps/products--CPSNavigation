# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
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
"""A ZODB Navigation
"""
from Acquisition import aq_parent, aq_inner
from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation

class ZODBNavigation(BaseNavigation):
    """Implement Finder interface for a ZODB."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    ### Finder interface
    def getObject(self, uid):
        try:
            obj = self.root.unrestrictedTraverse(uid)
        except KeyError:
            obj = None
        return obj

    def getUid(self, obj):
        # return something like 'cps/sections/folder'
        return obj.absolute_url(1)

    def isNode(self, obj):
        return obj.isPrincipiaFolderish

    def hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self.getChildren(obj, no_nodes, no_leaves))

    def getChildren(self, obj, no_nodes=0, no_leaves=0):
        children = obj.objectValues()
        if no_nodes:
            children = [child for child in children if not self.isNode(child)]
        if no_leaves:
            children = [child for child in children if self.isNode(child)]

        return children

    def getParent(self, obj):
        return aq_parent(aq_inner(obj))
