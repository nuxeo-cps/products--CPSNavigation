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

from Products.CMFCore.utils import getToolByName
from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation
from zLOG import LOG, DEBUG, ERROR

class CPSDirectoryNavigation(BaseNavigation):
    """Implement Finder interface for a CPSDirectory."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    def __init__(self, **kw):
        if not kw.get('context'):
            raise KeyError, 'No context provided.'
        if not kw.get('dir_name'):
            raise KeyError, 'No dir_name provided.'

        self._dir = getToolByName(kw['context'],
                                  'portal_directories')[kw['dir_name']]
        self._attrs = self._getAttrs(kw['context'])
        BaseNavigation.__init__(self, **kw)


    def _getAttrs(self, context):
        # return list of attributes
        attrs = [x['id'] for x in
                 context.getDirectoryResultFields(self._dir.getId(),
                                                  self._dir.title_field)]
        if self._dir.id_field not in attrs:
            attrs.append(self._dir.id_field)
        if self._dir.title_field not in attrs:
            attrs.append(self._dir.title_field)
        return attrs

    ### Finder interface
    def _getObject(self, uid):
        if not hasattr(self, 'root_uid') or uid == self.root_uid:
            return {'is_root':1, 'uid':uid}
        obj = self._dir._getEntry(uid)
        obj['the_uid'] = uid
        return obj

    def _getUid(self, obj):
        if not hasattr(self, 'root') or obj == self.root:
            return self.root_uid
        return obj.get(self._dir.id_field)

    def _isNode(self, obj):
        if obj == self.root:
            return 1
        return 0

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        if obj == self.root:
            return 1
        return 0

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        if obj == self.root:
            uids = self._dir.listEntryIds()
            return [self._getObject(uid) for uid in uids]
        return []

    def _getParentUid(self, uid):
        return None

    ### override Navigation
    def _search(self):
        key = self._dir.id_field
        query_pattern = self.request_form.get('query_uid', '').strip()
        if not query_pattern:
            return []
        query = {key:query_pattern}

        if self.debug:
            LOG('CPSDirectoryNavigation._search', DEBUG,
                'query=%s attrs=%s' % (query, self._attrs))

        res = self._dir.searchEntries(return_fields=self._attrs,
                                      **query)
        for r in res:
            r[1].update({'the_uid': r[0]})
        res = [r[1] for r in res]
        return res
