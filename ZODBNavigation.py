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
"""A CMF Finder
"""
from Acquisition import aq_parent, aq_inner
from interfaces.Finder import Finder
from Products.CMFCore.utils import getToolByName


class CMFFinder:
    """Implement Finder interface for a CMF site."""
    __implements__ = (Finder, )     # See Finder interface for method docstring

    ### Finder interface
    def setParams(self, **kw):
        self._param_ids = kw.keys()
        for k, v in kw.items():
            setattr(self, k, v)

    def isNode(self, obj):
        return obj.isPrincipiaFolderish

    def hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self.getChildren(obj, no_nodes, no_leaves))

    def getChildren(self, obj, no_nodes=0, no_leaves=0):
        children = obj.objectValues()
        if no_nodes:
            children = [child for child in children and not self.isNode(i)]
        if no_leaves:
            children = [child for child in children and self.isNode(i)]

        return children

    def getParents(self, obj):
        parents = []
        portal_url = getToolByName(obj, 'portal_url')
        portal = portal_url.getPortalObject()

        # find the first parent
        parent = obj
        while parent and not self.isNode(parent):
            parent = aq_parent(aq_inner(parent))

        if not(parent is obj):
            parents.append(parent)

        while parent and parent is not portal:
            parent = aq_parent(aq_inner(parent))
            parents.append(parent)

        return parents
