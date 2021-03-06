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
from Acquisition import aq_base, aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation
from urllib import unquote
from zLOG import LOG, DEBUG
from time import time

class ZODBNavigation(BaseNavigation):
    """Implement Finder interface for a ZODB."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    _v_wtool = None                     # workflow tool cache

    def __init__(self, **kw):
        if not kw.get('context'):
            raise KeyError, "No context provided."
        if not kw.get('current_uid') and not kw.get('root_uid'):
            # use the context
            kw['current_uid'] = kw['context'].absolute_url(1)
        if not kw.get('current_uid') and kw.get('root_uid'):
            kw['current_uid'] = kw['root_uid']
        if kw.get('current_uid') and not kw.get('root_uid'):
            kw['root_uid'] = kw['current_uid'].split('/')[0]
        setattr(self, 'context', kw['context'])
        BaseNavigation.__init__(self, **kw)

    ### Finder interface
    def _getObject(self, uid):
        try:
            obj = self.context.unrestrictedTraverse(unquote(uid))
        except KeyError:
            obj = None
        return obj

    def _getUid(self, obj):
        # return something like 'cps/sections/folder'
        return obj.absolute_url(1)

    def _isNode(self, obj):
        return aq_base(obj).isPrincipiaFolderish

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        children = obj.objectValues()
        if no_nodes:
            children = [child for child in children if not self._isNode(child)]
        if no_leaves:
            children = [child for child in children if self._isNode(child)]

        return children

    def _getParentUid(self, uid):
        obj = self._getObject(uid)
        parent = aq_parent(aq_inner(obj))
        # XXX perhaps we should use _filter to check is parent is viewable
        return self._getUid(parent)

    ### override Navigation
    def _filter(self, objs, mode='tree'):
        if self.debug:
            LOG('ZODBNavigation._filter', DEBUG, 'start')
        res = []
        if mode == 'listing':
            now = DateTime()
        obj_count = res_count = 0
        chrono_start = time()
        for obj in objs:
            obj_count +=1
            #common filtering
            obj_id = obj.getId()
            # XXX this filter to much removing folder like portal_*
            # even if they are not tools
            if obj_id.startswith('portal_'):
                continue
            if obj_id.startswith('.'):
                continue
            if obj_id in ('acl_users', 'Localizer',
                          'mimetypes_registry', 'Members'):
                continue
            if not _checkPermission('View', obj):
                continue

            if mode == 'tree':
                # conditional filtering
                if 'filter_tree_ptypes' in self._param_ids and \
                       self.filter_tree_ptypes:
                    portal_type = getattr(aq_base(obj), 'portal_type', None)
                    if portal_type not in self.filter_tree_ptypes:
                        continue
            elif mode == 'listing':
                # check effective/expire
                if not _checkPermission('Modify portal content', obj):
                    review_state = self._getWorkflowInfo(obj,
                                                         'review_state')
                    if review_state == 'published':
                        doc = obj.getContent()
                        if now < doc.effective() or now > doc.expires():
                            continue

                # conditional filtering
                if 'filter_listing_ptypes' in self._param_ids and \
                       self.filter_listing_ptypes:
                    portal_type = getattr(obj, 'portal_type', None)
                    if portal_type not in self.filter_listing_ptypes:
                        continue
            res_count += 1
            res.append(obj)
        chrono_stop = time()
        if self.debug:
            LOG('ZODBNavigation._filter', DEBUG, 'end\n'
                '\tfilter %s return %s in %.3fs\n' % (
                obj_count, res_count, chrono_stop - chrono_start,))

        return res

    def _getWorkflowInfo(self, obj, info):
        # Caching workflow tool
        if not self._v_wtool:
            self._v_wtool = getToolByName(self.context, 'portal_workflow')
        return self._v_wtool.getInfoFor(obj, info, 'nop')

    def _getReviewStateOrder(self, obj):
        # XXXX Warning this is hard coded status order !!
        review_state = self._getWorkflowInfo(obj, 'review_state')
        return {'nop':'0',
                'pending':'1',
                'published':'2',

                }.get(review_state, '0')

    def _getSortKey(self, obj, sort_by, mode='listing'):
        key = ''
        if mode == 'listing':
            key = '1'
            if self._isNode(obj):
                key = '0'
            if sort_by == 'review_state':
                key += self._getReviewStateOrder(obj)
            elif sort_by == 'date':
                key += str(self._getWorkflowInfo(obj ,'time'))

        if sort_by == 'id':
            return key + obj.getId()
        else:
            try:
                key += obj.title_or_id().lower()
            except AttributeError:
                pass
        return key


    def _sort(self, objs, mode='tree'):
        sort_by = None
        if mode == 'tree':
            if 'sort_tree_by' in self._param_ids:
                sort_by = self.sort_tree_by
                if 'sort_tree_direction' in self._param_ids:
                    direction = self.sort_tree_direction
        if mode == 'listing':
            if 'sort_listing_by' in self._param_ids:
                sort_by = self.sort_listing_by
                if 'sort_listing_direction' in self._param_ids:
                    direction = self.sort_listing_direction
        if sort_by:
            res = [(self._getSortKey(x, sort_by, mode), x ) for x in objs]
            res.sort() # tuples compare "lexicographically"
            if direction == 'desc':
                res.reverse()
            objs = [ obj[1] for obj in res]

        return objs
