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
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from types import StringType
from ZODBNavigation import ZODBNavigation
from Acquisition import aq_base, aq_parent, aq_inner
from zLOG import LOG, DEBUG
from time import time
from types import IntType

class CPSNavigation(ZODBNavigation):
    """Implement Finder interface for a CPS.
    the tree contains portal_tree node,
    the listing are normal object."""

    sort_limit = 100

    def __init__(self, **kw):
        # root and current are cps tree node object !
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
        ptrees = getToolByName(kw['context'], 'portal_trees')

        # Prefix for the tree if specified
        prefix = kw.get('prefix')
        self._cps_tree = ptrees[kw['root_uid']].getList(
            prefix=prefix,
            filter=1)

        ZODBNavigation.__init__(self, **kw)
        self._cps_tree_fixture()


    def _cps_tree_fixture(self):
        if self.root is None:
            # you don't have access to root_uid:
            # build a fake root object linking to available children
            items = self._cps_tree
            if not items or len(items) == 0:
                return
            local_rpath = items[0]['rpath'] + '/'
            root_children = [items[0]['rpath']]
            for item in items[1:]:
                if not (item['rpath'] + '/').startswith(local_rpath):
                    local_rpath = item['rpath'] + '/'
                    root_children.append(item['rpath'])
            self.root =  {'rpath': self.root_uid,
                          'nb_children': len(root_children),
                          'children': root_children}
            if self.current_uid == self.root_uid:
                self.current = items[0]
                self.current_uid = items[0]['rpath']
            # force root hidding
            self.include_root = 0


    ### Finder interface
    def _getObject(self, uid):
        """uid is an rpath, return a portal_tree node."""
        for n in self._cps_tree:
            if n['rpath'] == uid:
                return n
        if hasattr(self, 'root_uid') and self.root_uid == uid:
            return getattr(self, 'root', None)
        return None

    def _getUid(self, obj):
        """obj is a portal_tree node, return the rpath."""
        uid = None
        try:
            uid = obj['rpath']
        except (TypeError, KeyError):
            LOG('CPSNavigation._getUid', DEBUG, '')
            pass
        return uid

    def _isNode(self, obj):

        # XXX comment please
        if type(obj) is DictType:
            return 1

        # If we defined a filter explicitly
        if 'filter_listing_ptypes' in self._param_ids and \
               self.filter_listing_ptypes:
            if obj.portal_type in self.filter_listing_ptypes:
                return 1
            else:
                return 0

        # Otherweise, check the proxy_type (folder / folderishdocument)
        if getattr(obj, 'portal_type'):
            ti = getattr(obj.portal_types, obj.portal_type)
            if ti.meta_type == 'CPS Flexible Type Information':
                display = getattr(ti,
                                  'cps_display_as_document_in_listing',
                                  0)
                proxy_type = getattr(ti,
                                     'cps_proxy_type',
                                     'document')
                return proxy_type in ['folder',
                                      'folderishdocument'] and not display

        # Not a CPS Flexible Type Information
        return obj.isPrincipiaFolderish

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        """obj is a portal_tree node."""
        return obj.get('nb_children')

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        """obj is either a real object for listing or a tree_node when
        called by getTree."""
        if not obj:
            return []

        if mode == 'tree':
            # we are called by a getTree so we use portal tree
            # we assume we want nodes only
            if not obj['nb_children']:
                return []
            if obj.has_key('children'): # only fake root has children key
                return [x for x in self._cps_tree if \
                        x['rpath'] in obj['children']]
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
        if mode == 'listing' and not self.search:
            return ZODBNavigation._filter(self, objs, mode)
        elif mode == 'tree':
            if 'filter_tree_ptypes' in self._param_ids and \
                   self.filter_tree_ptypes:
                objs = [obj for obj in objs
                        if obj['portal_type'] in self.filter_tree_ptypes]
        return objs

    def _sort(self, objs, mode='tree'):
        if mode == 'listing' and not self.search:
            return ZODBNavigation._filter(self, objs, mode)
        return objs

    def _buildQuery(self, query_in, portal_path):
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
            if self.no_nodes:
                query['cps_filter_sets'] = {'query' : ('searchable', 'leaves'),
                                            'operator' : 'and'}
            if 'filter_listing_ptypes' in self._param_ids and \
                   self.filter_listing_ptypes:
                query['portal_type'] = self.filter_listing_ptypes

        # handle sorting
        if 'sort_listing_by' in self._param_ids:
            if self.sort_listing_by and not query_in.has_key('sort-on'):
                # for compatibility with cpsdefault search
                sort_by = self.sort_listing_by
                if sort_by in ('title', 'date'):
                    sort_by = sort_by.capitalize()
                elif sort_by == 'status':
                    sort_by = 'review_state'
                elif sort_by == 'author':
                    sort_by = 'Creator'
                query['sort-on'] = sort_by
                if 'sort_listing_direction' in self._param_ids:
                    direction = self.sort_listing_direction
                    if direction.startswith('desc'):
                        query['sort-order'] = 'reverse'
                if self.sort_limit:
                    query['sort-limit'] = self.sort_limit

        return query


    def _search(self):
        """Search repository."""
        if not hasattr(self, 'query'):
            return []

        ctool = getToolByName(self.context, 'portal_catalog')
        portal = aq_parent(aq_inner(ctool))
        portal_path = '/' + ctool.getPhysicalPath()[1] + '/'

        query = self._buildQuery(getattr(self, 'query', {}), portal_path)
        LOG('BaseNavigation._search', DEBUG, 'start\n'
            '\tquery = %s\n' % (query))
        if not query:
            return []

        chrono_start = time()
        brains = ctool(**query)
        chrono_stop = time()

        LOG('BaseNavigation._search', DEBUG, 'end\n'
            '\tcatalog found %s document brains in %7.3fs\n' % (
            len(brains), chrono_stop - chrono_start))

        return brains
