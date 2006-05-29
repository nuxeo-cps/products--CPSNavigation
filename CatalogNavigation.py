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

XXXX Warning this code is not uptodate with CPS Core > 3.18.0
This means that it does not support i18n document.
Do not use this navigation class with translated folder or document.
"""
from types import DictType
from time import time

from zLOG import LOG, DEBUG
from DateTime import DateTime
from Acquisition import aq_base, aq_parent, aq_inner
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission
from Products.CMFCore.permissions import AccessInactivePortalContent

from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation


class CatalogNavigation(BaseNavigation):
    """Implement Finder interface using the portal_catalog."""

    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    sort_limit = 100
    find_root_depth_max = 4
    node_depth_max = 0
    _search_count = 0

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
        self.portal_path_len = len(self.portal_path)
        BaseNavigation.__init__(self, **kw)


    #
    # Finder interface
    #
    def _getObject(self, uid):
        """Return an object using uid.

        uid is a getRelativeUrl like sections/foo
        the object is a brain or a catalog metadata mapping
        note that uid for catalog is the physical path like /cps/sections/foo
        rid is a catalog record id
        """
        # XXX AT: this does not work using the Lucene catalog
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
            uid = self.ctool._catalog.paths[rid][self.portal_path_len:]
        return uid

    def _isNode(self, obj):
        """Do nothing as we use search filter for nodes and leaves
        this is only used by BaseNavigation explore nodes so return 1
        """
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        return len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        if not obj:
            return []
        uid = self._getUid(obj)
        luid = self.portal_path + uid

        # don't search if current node is already at the node_depth_max
        if mode == 'tree' and self.node_depth_max:
            if (uid.count('/')+1) >= self.node_depth_max:
                return []
        # search
        self.query = {'container_path': luid}
        if no_nodes:
            # xxx TODO impl
            pass

        if uid == self.root_uid and mode == 'tree':
            return self._findRoots()
        return self._search(mode=mode)

    def _getParentUid(self, uid):
        return '/'.join(uid.split('/')[:-1])


    #
    # override Navigation
    #
    def _search(self, mode='listing'):
        """Search repository.
        """
        self._search_count += 1
        if not hasattr(self, 'query'):
            return []

        portal = aq_parent(aq_inner(self.ctool))
        portal_path = '/' + self.ctool.getPhysicalPath()[1] + '/'

        query = self._buildQuery(getattr(self, 'query', {}),
                                 portal_path, mode)
        LOG('CatalogNavigation._search', DEBUG, 'start\n'
            '\tquery = %s\n' % (query))
        if not query:
            return []

        chrono_start = time()
        try:
            brains = ZCatalog.searchResults(self.ctool, None, **query)
        except ParseError:
            brains = []
        chrono_stop = time()

        LOG('CatalogNavigation._search', DEBUG, 'end\n'
            '\tcatalog found %s document brains in %7.3fs\n' % (
            len(brains), chrono_stop - chrono_start))

        return brains


    #
    # Private
    #
    def _findRoots(self):
        """Discover roots that are not direct children of root_uid.
        """
        # first get visible children
        children = self._search(mode='tree')

        # then get all children
        query = self._buildQuery(getattr(self, 'query', {}),
                                 self.portal_path, 'tree', viewable=0)
        LOG('CatalogNavigation._findRoots', DEBUG, 'start\n'
            '\tquery = %s\n' % (query))
        all_children = ZCatalog.searchResults(self.ctool, None, **query)
        LOG('CatalogNavigation._findRoots', DEBUG, 'found %s items' %
            len(all_children))

        if len(all_children) == len(children):
            # all children are visible
            return children

        # we are building the children list
        # assuming that the root is not accessible
        self.include_root = 0
        depth_min = len(self.root_uid.split('/')) + 2
        depth_max = depth_min + self.find_root_depth_max - 2

        pathes_viewable = [x.relative_path for x in children]
        pathes_to_explore = [self.portal_path + x.relative_path \
                             for x in all_children if \
                             x.relative_path not in pathes_viewable]
        LOG('CatalogNavigation._findRoots', DEBUG, 'explore %s' %
            pathes_to_explore)

        query = {'path': pathes_to_explore}
        query['relative_path_depth'] = {'query': (depth_min, depth_max),
                                        'range': 'min:max'}
        query['sort-on'] = 'relative_path'
        self.query = query
        brains = self._search(mode='tree')
        # extract roots
        items = []
        last_root = None
        for b in brains:
            current_container = b.relative_path[:-len(b.getId)]
            if last_root and current_container.startswith(last_root):
                continue
            last_root = b.relative_path + '/'
            items.append(b)

        # add new roots to children
        if len(items):
            items = [x for x in children] + items

        LOG('CatalogNavigation._findRoots', DEBUG, 'found %s' % (
            [x.relative_path for x in items]))

        return items

    def _buildQuery(self, query_in, portal_path, mode='listing',
                    viewable=1):
        """Query builder.
        """
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
            if viewable:
                user = _getAuthenticatedUser(self)
                query['allowedRolesAndUsers'] = self.ctool._listAllowedRolesAndUsers(user)
                if 'Manager' in query['allowedRolesAndUsers']:
                    # manager powa
                    del query['allowedRolesAndUsers']
            if mode == 'listing':
                if not _checkPermission(AccessInactivePortalContent, self):
                    base = aq_base(self)
                    now = DateTime()
                    query['effective_range'] = now
                if self.no_nodes:
                    query['cps_filter_sets'] = {'query': ('searchable', 'leaves'),
                                                'operator': 'and'}
                if 'filter_listing_ptypes' in self._param_ids and \
                       self.filter_listing_ptypes:
                    query['portal_type'] = self.filter_listing_ptypes
            elif mode == 'tree':
                if 'filter_tree_ptypes' in self._param_ids and \
                       self.filter_tree_ptypes:
                    query['portal_type'] = self.filter_tree_ptypes
                if 'filter_tree_language' in self._param_ids and (
                        self.filter_tree_language):
                    query['Language'] = self.filter_tree_language
                if self.node_depth_max and \
                       not query.has_key('relative_path_depth'):
                    query['relative_path_depth'] = {
                        'query': self.node_depth_max,
                        'range': 'max'}

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


