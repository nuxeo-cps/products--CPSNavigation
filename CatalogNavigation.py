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
"""A CPS Navigation using the catalog
"""

from types import DictType
from Products.CMFCore.utils import getToolByName
from types import StringType
from BaseNavigation import BaseNavigation
from Acquisition import aq_base, aq_parent, aq_inner
from zLOG import LOG, DEBUG
from time import time
from types import IntType
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission
from Products.CMFCore.CMFCorePermissions import AccessInactivePortalContent
from DateTime import DateTime



class CatalogNavigation(BaseNavigation):
    """Implement Finder interface using the portal_catalog."""

    sort_limit = 100

    def __init__(self, **kw):
        if not kw.get('context'):
            raise KeyError, "No context provided."
        if not kw.get('current_uid') and not kw.get('root_uid'):
            # use the context
            purl = getToolByName(kw['context'], 'portal_url')
            kw['current_uid'] = purl.getRelativeUrl(kw['context'])
        if not kw.get('current_uid') and kw.get('root_uid'):
            kw['current_uid'] = kw['root_uid']
        if kw.get('current_uid') and not kw.get('root_uid'):
            kw['root_uid'] = kw['current_uid'].split('/')[0]
        self.ctool = getToolByName(kw['context'], 'portal_catalog')
        self.portal_path = '/' + self.ctool.getPhysicalPath()[1] + '/'
        BaseNavigation.__init__(self, **kw)

    ### Finder interface
    # uid for catalogNavigation is a getRelativeUrl like sections/foo
    # the object is a brain or a catalog metadata mapping
    # note that uid for catalog is the physicalPath /cps/sections/foo
    # rid is a catalog record id
    def _getObject(self, uid):
        rid = self.ctool._catalog.uids.get(self.portal_path+uid)
        if not rid:
            return None
        res = self.ctool.getMetadataForRID(rid)
        res['uid'] = uid
        res['rid'] = rid
        return res

    def _getUid(self, obj):
        """obj is catalog metadata return rid."""
        if type(obj) is DictType:
            uid = obj.get('uid')
        else:
            # obj is a brain
            rid = obj.getRID()
            uid = self.ctool._catalog.paths[rid][len(self.portal_path):]
        return uid

    def _isNode(self, obj):
        # XXX TODO impl
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        return len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        if not obj:
            return []
        uid = self._getUid(obj)
        luid = self.portal_path + uid
        level = len(luid.split('/'))
        child_level = level + 1
        # search
        self.query = {'container_path': luid}
        if no_nodes:
            # xxx TODO impl
            pass
        return self._search(mode=mode)

    def _getParentUid(self, uid):
        obj = self._getObject(uid)
        return '/'.join(uid.split('/')[:-1])

    ### override Navigation

    def _buildQuery(self, query_in, portal_path, mode='listing'):
        query = {}
        date_suffix = '_usage'

        if not query_in:
            return query

        for k, v in query_in.items():
            # skip date usage key without date
            if k.endswith(date_suffix):
                k_prefix = k[:-len(date_suffix)]
                if not query_in.get(k_prefix):
                    v = None
            if v:
                # skip this criteries, they are added by catalog tool
                if k in ('expires', 'effective',
                         'expires_usage', 'effective_usage'):
                    continue

                # title search
                if k == 'Title':
                    # we search on the ZCTextIndex,
                    # Title index is a FieldIndex only used for sorting
                    query['ZCTitle'] = v
                # compatibility with cpsdefault search
                elif k == 'folder_prefix' and not query_in.has_key('path'):
                    query['path'] = portal_path + v
                elif k == 'start_date' and not query_in.has_key('start'):
                    query['start'] = {'query' : v,
                                      'range' : 'min'}
                elif k == 'end_date' and not query_in.has_key('end'):
                    query['end'] = {'query' : v,
                                    'range' : 'max'}
                else:
                    query[k] = v

        if query or self.allow_empty_search:
            # this is a set of searchable document
            # not located in the repository, without any '.xx'
            query['cps_filter_sets'] = 'searchable'
            # filter viewable document
            user = _getAuthenticatedUser(self)
            query[
                'allowedRolesAndUsers'] = self.ctool._listAllowedRolesAndUsers(
                user)

            if mode == 'listing':
                if not _checkPermission(AccessInactivePortalContent, self):
                    base = aq_base(self)
                    now = DateTime()
                    query['effective_range'] = now
                if self.no_nodes:
                    query['cps_filter_sets'] = {'query' :
                                                ('searchable', 'leaves'),
                                                'operator' : 'and'}
                if 'filter_listing_ptypes' in self._param_ids and \
                       self.filter_listing_ptypes:
                    query['portal_type'] = self.filter_listing_ptypes
            elif mode == 'tree':
                if 'filter_tree_ptypes' in self._param_ids and \
                       self.filter_tree_ptypes:
                    query['portal_type'] = self.filter_tree_ptypes

        # handle sorting
        if not query.has_key('sort-on'):
            sort_by = direction = None
            if mode == 'listing':
                if 'sort_listing_by' in self._param_ids and \
                       self.sort_listing_by:
                    sort_by = self.sort_listing_by
                    if 'sort_listing_direction' in self._param_ids and \
                       self.sort_listing_direction:
                        direction = self.sort_listing_direction
                        if direction.startswith('desc'):
                            query['sort-order'] = 'reverse'
            elif mode == 'tree':
                if 'sort_tree_by' in self._param_ids and \
                       self.sort_tree_by:
                    sort_by = self.sort_tree_by
                    if 'sort_tree_direction' in self._param_ids and \
                       self.sort_tree_direction:
                        direction = self.sort_tree_direction
                        if direction.startswith('desc'):
                            query['sort-order'] = 'reverse'
            if sort_by:
                # for compatibility with cpsdefault search
                if sort_by in ('title', 'date'):
                    sort_by = sort_by.capitalize()
                elif sort_by == 'status':
                    sort_by = 'review_state'
                elif sort_by == 'author':
                    sort_by = 'Creator'
                query['sort-on'] = sort_by
                if self.sort_limit:
                    query['sort-limit'] = self.sort_limit

        return query


    def _search(self, mode='listing'):
        """Search repository."""
        if not hasattr(self, 'query'):
            return []

        ctool = getToolByName(self.context, 'portal_catalog')
        portal = aq_parent(aq_inner(ctool))
        portal_path = '/' + ctool.getPhysicalPath()[1] + '/'

        query = self._buildQuery(getattr(self, 'query', {}),
                                 portal_path, mode)
        LOG('CatalogNavigation._search', DEBUG, 'start\n'
            '\tquery = %s\n' % (query))
        if not query:
            return []

        chrono_start = time()
        brains = ZCatalog.searchResults(ctool, None, **query)
        chrono_stop = time()

        LOG('CatalogNavigation._search', DEBUG, 'end\n'
            '\tcatalog found %s document brains in %7.3fs\n' % (
            len(brains), chrono_stop - chrono_start))

        return brains
