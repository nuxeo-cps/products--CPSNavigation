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
"""A CPSDirectory Navigation
"""
from zLOG import LOG, DEBUG, ERROR

from Products.CMFCore.utils import getToolByName
from Products.CPSNavigation.interfaces.IFinder import IFinder
from Products.CPSNavigation.BaseNavigation import BaseNavigation


class CPSDirectoryNavigation(BaseNavigation):
    """Implement Finder interface for a CPSDirectory."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    def __init__(self, **kw):
        if kw.get('context') is None:
            raise KeyError, 'No context provided.'
        if kw.get('dir_name') is None:
            raise KeyError, 'No dir_name provided.'

        self._dir = getToolByName(kw['context'],
                                  'portal_directories')[kw['dir_name']]
        # if root is not specified use directory as root
        if not kw.get('root_uid') or kw['root_uid'] == kw['dir_name']:
            kw['root_uid'] = kw['dir_name']
            self.root_uid = kw['dir_name']
            self.root = {'is_root':1, 'uid':self.root_uid}
            self.use_a_fake_root = True
        else:
            self.use_a_fake_root = False
        self._attrs = self._getAttrs(kw['context'])
        BaseNavigation.__init__(self, **kw)

    def _getAttrs(self, context):
        """Return list of attributes that is used in the result list."""
        attrs = [x['id'] for x in
                 context.getDirectoryResultFields(self._dir.getId(),
                                                  self._dir.title_field)]
        if self._dir.id_field not in attrs:
            attrs.append(self._dir.id_field)
        if self._dir.title_field not in attrs:
            attrs.append(self._dir.title_field)
        return attrs


    # ------------------------------------------------------------
    # Finder interface
    #
    def _getObject(self, uid):
        if not uid:
            return None
        if self.use_a_fake_root and uid == self.root_uid:
            # return the fake root object
            return self.root
        obj = self._dir._getEntry(uid)
        obj['the_uid'] = uid
        return obj

    def _getUid(self, obj):
        if self.use_a_fake_root and obj is self.root:
            # return the fake root_uid
            return self.root_uid
        return obj.get(self._dir.id_field)

    def _isNode(self, obj):
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        if obj is self.root:
            return 1
        return len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        if self.use_a_fake_root and obj is self.root:
            # list all entries for fake root
            uids = self._dir.listEntryIds()
            return [self._getObject(uid) for uid in uids]
        if not self._dir._isHierarchical():
            return []
        children = self._dir._listChildrenEntryIds(self._getUid(obj))
        LOG('CPSDirectoryNavigation._search', DEBUG,
            'getchildren %s = \n%s' % (self._getUid(obj), children))
        return [self._getObject(uid) for uid in children]

    def _getParentUid(self, uid):
        ret = None
        if uid == self.root_uid:
            return ret
        if self._dir._isHierarchical():
            ret = self._dir._getParentEntryId(uid)
        if self.use_a_fake_root and ret is None:
            # return the fake root_uid
            return self.root_uid
        return ret

    # ------------------------------------------------------------
    # override Navigation
    def _search(self):
        key = self._dir.id_field
        title = self._dir.title_field
        query_pattern = self.request_form.get('query_uid', '').strip()
        if not query_pattern:
            return []
        query = {title:query_pattern}

        if self.debug:
            LOG('CPSDirectoryNavigation._search', DEBUG,
                'query=%s attrs=%s' % (query, self._attrs))

        res = self._dir.searchEntries(return_fields=self._attrs,
                                      **query)
        for r in res:
            r[1].update({'the_uid': r[0]})
        res = [r[1] for r in res]
        return res
