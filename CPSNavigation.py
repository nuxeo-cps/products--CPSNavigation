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
"""A CPS Navigation using portal_tree
"""
from types import DictType
from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from interfaces.IFinder import IFinder
from ZODBNavigation import ZODBNavigation
from zLOG import LOG, DEBUG

class CPSNavigation(ZODBNavigation):
    """Implement Finder interface for a CPS.
    the tree contains portal_tree node,
    the listing are normal object."""

    def __init__(self, **kw):
        #root and current are cps tree node object !
        if not kw.get('current_uid'):
            raise KeyError, "No current_uid provided."
        if not kw.get('root_uid'):
            raise KeyError, "No root_uid provided."
        if not kw.get('context'):
            raise KeyError, "No context provided."

        ptrees = getToolByName(kw['context'], 'portal_trees')
        self._cps_tree = ptrees[kw['root_uid']].getList(filter=1)
        ZODBNavigation.__init__(self, **kw)

    ### Finder interface
    def _getObject(self, uid):
        """uid is an rpath, return a portal_tree node."""
        for n in self._cps_tree:
            if n['rpath'] == uid:
                return n
        return None

    def _getUid(self, obj):
        """obj is a portal_tree node, return the rpath."""
        return obj['rpath']

    def _isNode(self, obj):
        if type(obj) is DictType:
            return 1
        # XXX check portal types for display_as_document_in_listing
        # ret obj.isPrincipiaFolderish and not display_as_document_in_listing
        return obj.isPrincipiaFolderish

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        """obj is a portal_tree node."""
        return obj.get('nb_children')

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        """obj is either a real object for listing or a tree_node when
        called by getTree."""
        if mode == 'tree':
            # we are called by a getTree so we use portal tree
            # we assume we want nodes only
            if not obj['nb_children']:
                return []
            children_prefix = obj['rpath'] + '/'
            children_depth = obj['depth'] + 1
            return [x for x in self._cps_tree if \
                    x['depth'] == children_depth and \
                    x['rpath'].startswith(children_prefix)]

        # for the listing use the ZODB
        lobj = obj
        if type(obj) is DictType:
            lobj = self.context.unrestrictedTraverse(self._getUid(obj))
        return ZODBNavigation._getChildren(self, lobj, no_nodes, no_leaves)

    def _getParentUid(self, uid):
        return '/'.join(uid.split('/')[:-1])

    ### override Navigation
    def _filter(self, objs, mode='tree'):
        if mode == 'tree':
            return objs
        return ZODBNavigation._filter(self, objs, mode)
