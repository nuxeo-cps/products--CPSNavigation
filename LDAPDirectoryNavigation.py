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
"""A LDAPDirectory Navigation
"""
from types import DictType
from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation
from zLOG import LOG, DEBUG, ERROR

class LDAPDirectoryNavigation(BaseNavigation):
    """Implement Finder interface for a LDAPDirectory."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    def __init__(self, **kw):
        if not kw.get('context'):
            raise KeyError, 'No context provided.'
        if not kw.get('dir_name'):
            raise KeyError, 'No dir_name provided.'
        self._dir = getToolByName(kw['context'],
                                  'portal_directories')[kw['dir_name']]
        BaseNavigation.__init__(self, **kw)


    ### Finder interface
    def _getObject(self, uid):
        # return an mapping of a directory entry
        obj = None
        try:
            obj = self._dir.getEntryByDN(uid)
        except ValueError:
            pass
        return obj

    def _getUid(self, obj):
        # return something like
        # 'ou=direction des musees de france,ou=culture,o=gouv,c=fr
        if type(obj) is DictType:
            LOG('XXXXX', DEBUG, obj['dn'])
            return obj['dn']
        return None

    def _isNode(self, obj):
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        dn = self._getUid(obj)
        dir = self._dir
        res = dir._delegate.search(base=dn,
                                   scope=1,
                                   filter=dir.objectClassFilter(),
                                   attrs=['dn'])
        if res['exception']:
            LOG('LDAPDirectory', ERROR, 'Error talking to server: %s'
                % res['exception'])
            raise ValueError(res['exception']) # XXX do better ?

        children = [self._getObject(x['dn']) for x in res['results']]
        children = filter(None, children)
        if no_nodes:
            children = [child for child in children if not self._isNode(child)]

        return children

    def _getParent(self, obj):
        dn = self._getUid(obj)
        parent_dn = dn.split(',', 1)[1]
        return self._getObject(parent_dn)
