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
from Products.CMFCore.utils import getToolByName
from ZODBNavigation import ZODBNavigation
from zLOG import LOG, DEBUG
from time import clock

class CPSNavigation(ZODBNavigation):
    """Implement Finder interface for a CPS.
    the tree contains portal_tree node,
    the listing are normal object."""

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
        self._cps_tree = ptrees[kw['root_uid']].getList(filter=1)
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
        if mode == 'tree':
            return objs
        return ZODBNavigation._filter(self, objs, mode)


    def _clean_query(self, query_in):
        catalog_query = {}
        cps_query = {}
        date_suffix = '_usage'
        if not query_in:
            return catalog_query, cps_query

        for k, v in query_in.items():
            # skip date usage key without date
            if k.endswith(date_suffix):
                k_prefix = k[:-len(date_suffix)]
                if not query_in.get(k_prefix):
                    v = None
            if v:
                catalog_query[k] = v

        for k in ('folder_prefix', 'start_date', 'end_date',
                  'review_state'):
            if catalog_query.has_key(k):
                cps_query[k] = catalog_query[k]
                del catalog_query[k]

        if catalog_query:
            portal_path = getToolByName(self.context,
                                        'portal_url').getPortalPath()
            catalog_query['path'] = portal_path + '/portal_repository/'
            if 'filter_listing_ptypes' in self._param_ids and \
                       self.filter_listing_ptypes:
                catalog_query['portal_type'] = self.filter_listing_ptypes

        return catalog_query, cps_query

    def _search(self):
        """Search repository."""
        if not hasattr(self, 'query'):
            return []

        catalog_query, cps_query = self._clean_query(
            getattr(self, 'query', {}))
        LOG('BaseNavigation._search', DEBUG, 'start\n'
            '\tcatalog_query = %s\n'
            '\tcps_query = %s'% (catalog_query, cps_query))
        if not catalog_query:
            return []

        proxy_count = 0
        catalog = getToolByName(self.context, 'portal_catalog')
        ptool = getToolByName(self.context, 'portal_proxies')
        wtool = getToolByName(self.context, 'portal_workflow')
        review_state = cps_query.get('review_state')
        start_date = cps_query.get('start_date')
        end_date = cps_query.get('end_date')

        # catalog search
        chrono_start = clock()
        doc_brains = catalog(**catalog_query)
        chrono_step1 = clock()

        # proxy search
        items = []
        for doc_brain in doc_brains:
            doc_id = doc_brain.getPath().split('/')[-1]
            proxy_infos = ptool.getProxiesFromObjectId(
                doc_id, proxy_rpath_prefix=cps_query.get('folder_prefix'))
            for proxy_info in proxy_infos:
                proxy_count += 1
                proxy = proxy_info['object']
                # status filtering
                if (review_state and
                    wtool.getInfoFor(proxy,
                                     'review_state',
                                     'nostate') != review_state):
                    continue
                # event start/end filtering
                if start_date and end_date:
                    doc = proxy.getContent()
                    sd = ed = 0
                    if hasattr(doc.aq_explicit, 'start'):
                        if callable(doc.start):
                            sd = doc.start()
                        else:
                            sd = doc.start
                    if hasattr(doc.aq_explicit, 'end'):
                        if callable(doc.end):
                            ed = doc.end()
                        else:
                            ed = doc.end
                    if not sd or not ed:
                        continue
                    if (sd - end_date > 0) or (start_date - ed > 0):
                        continue
                # get one
                items.append(proxy)

        chrono_stop = clock()
        LOG('BaseNavigation._search', DEBUG, 'end\n'
            '\tcatalog found %s document brains in %.3fs\n'
            '\tgetting %s proxies and filter in %.3fs\n'
            '\tsearch result: %s proxies found in %.3fs\n' % (
            len(doc_brains), chrono_step1 - chrono_start,
            proxy_count, chrono_stop - chrono_step1,
            len(items), chrono_stop - chrono_start,))

        return items
