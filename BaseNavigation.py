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
"""A Navigation class

   Used to build Navigation screen like tree + listing
"""
from ZTUtils import Batch
from types import IntType
from time import time
from zLOG import LOG, DEBUG


class BaseNavigation:
    """This is a Base class for other Navigation class.

    To write your navigation class you have to inherit from BaseNavigation
    and implement the IFinder interface.
    """
    no_leaves = 0
    no_nodes = 0
    batch_size = 15
    batch_orphan = 0
    batch_item_max = 100
    include_root = 1
    expand_all = 0
    debug = 1
    search = 0
    allow_empty_search = 0
    query_uid = ''
    request_form = {}

    def __init__(self, **kw):
        """Init the navigation.

        Required kw:
          root or root_uid       - the root object
          current or current_uid - the current position
        """
        kw_keys = kw.keys()
        if kw.get('root'):
            kw['root_uid'] = self._getUid(kw['root'])
        elif kw.get('root_uid'):
            kw['root'] = self._getObject(kw['root_uid'])
        else:
            raise KeyError, "No root or root_uid provided."

        if kw.get('current'):
            kw['current_uid'] = self._getUid(kw['current'])
        elif kw.get('current_uid'):
            kw['current'] = self._getObject(kw['current_uid'])

        if not kw.get('current') or not kw.get('current_uid'):
            kw['current'] = kw['root']
            kw['current_uid'] = kw['root_uid']

        if not kw['current_uid']:
            raise KeyError, "current_uid is empty. %s" % str(kw)
        self._setParams(**kw)

    def _setParams(self, **kw):
        """Setting navigation properties.
        """
        self._param_ids = kw.keys()
        for k, v in kw.items():
            setattr(self, k, v)
        if self.debug:
            LOG('BaseNavigation._setParams', DEBUG, str(kw))

    def _getParams(self):
        """Return the navigation properties."""
        res = {}
        for k in self._param_ids:
            res[k] = getattr(self, k)
        return res

    def _exploreNode(self, obj, level, is_last_child, path, flat_tree):
        if not obj:
            return
        obj_uid = self._getUid(obj)
        if not obj_uid:
            return
        node = {'uid': obj_uid,
                'object': obj,
                'level': level,
                'is_current': obj_uid == self.current_uid,
                'is_last_child': is_last_child,
                }
        if self.debug > 1:
            LOG('BaseNavigation._exploreNode', DEBUG, str(node))
        if not self.expand_all and obj_uid not in path:
            if self._isNode(obj) and \
               self._hasChildren(obj, no_leaves=1):
                node['has_children'] = 1
            else:
                node['has_children'] = 0
            flat_tree.append(node)
        else:
            children = self._getChildren(obj, no_leaves=1, mode='tree')
            children = filter(None, children)
            children = self._filter(children, mode='tree')
            children = self._sort(children, mode='tree')
            node['is_open'] = 1
            if self.expand_all and obj_uid not in path:
                node['is_open'] = 0
            node['children'] = children
            if len(children):
                node['has_children'] = 1
            else:
                node['has_children'] = 0
            flat_tree.append(node)
            for child in children:
                if child is children[-1]:
                    is_last_child = 1
                else:
                    is_last_child = 0
                self._exploreNode(child, level+1, is_last_child,
                                  path, flat_tree)

    def _getParentUids(self, uid, include_uid=1):
        """Return a list of parents uids from root to uid.

        uid is append to the list if include_uid"""
        res = []
        if include_uid:
            res = [uid]
        parent_uid = uid
        while parent_uid and parent_uid != self.root_uid:
            parent_uid = self._getParentUid(parent_uid)
            if parent_uid:
                res.append(parent_uid)
        res.reverse()
        if self.debug:
            LOG('BaseNavigation._getParentUids(%s)' % uid,
                DEBUG, 'return : ' + str(res))

        return res

    def getTree(self):        
        """Return a flat Tree structure easily processed in ZPT."""

        chrono_start = time()
        # compute the path to current
        path = self._getParentUids(self.current_uid)

        # explore tree using path
        tree = []
        self._exploreNode(self._getObject(path[0]), 0, 0, path, tree)

        # compute vertical lines and state of the node
        shift = 0
        if not self.include_root:
            tree = tree[1:]
            shift = 1
        lines = []
        lv = lv_ = 0
        for node in tree:
            lv = node['level'] - shift
            is_last_child = node.get('is_last_child')
            if is_last_child:
                value = 2
            else:
                value = 1
            if lv > lv_:
                lines.append(value)
            else:
                if lv < lv_:
                    lines = lines[:lv - lv_]
                if lv:
                    lines[-1] = value

            node['lines'] = tuple(lines)
            if is_last_child and lines:
                lines[-1] = 0
            lv_ = lv
            if node.get('is_open'):
                node['state'] = 'open'
            elif node.get('has_children'):
                node['state'] = 'closed'
            else:
                node['state'] = 'node'
        chrono_stop = time()

        LOG('BaseNavigation.getTree', DEBUG, 'end\n'
            '\ttime elapsed %7.3fs\n' % (
             chrono_stop - chrono_start))
        return tree

    def getListing(self):
        """Return a Listing structure and batch information."""
        chrono_start = time()
        res = self._searchItems()
        res = self._filter(res, mode='listing')
        res = self._sort(res, mode='listing')
        # XXX batching should be refactored
        # this is just a port of cpsdefault getBatch..
        length = len(res)
        batch_start = self.request_form.get('b_start', 0)
        if not self.batch_item_max or self.batch_item_max > length:
            res = Batch(res, self.batch_size, batch_start, self.batch_orphan)
            batch_length = length
        else:
            batch_length = self.batch_item_max
            if batch_start > batch_length:
                batch_start = 0
            res = Batch(res[:batch_length],
                        self.batch_size, batch_start, self.batch_orphan)

        nb_pages = batch_length / float(self.batch_size)
        if type(nb_pages) is not IntType and nb_pages > 1:
            nb_pages = int(nb_pages) + 1
        else:
            nb_pages = 0
        stop = batch_start + self.batch_size
        if stop > length:
            stop = length
        current = [0, 1]
        pages = []
        j = 0
        for i in range(nb_pages):
            pages.append(j)
            if batch_start == j:
                current = [i + 1, j]
            j += self.batch_size
        if current[0] > 1:
            previous = current[1] - self.batch_size
        else:
            previous = None
        if current[0] != nb_pages:
            next = current[1] + self.batch_size
        else:
            next = None

        batch_info = {'nb_pages': nb_pages,
                      'pages': pages,
                      'start': batch_start + 1,
                      'stop': stop,
                      'length': length,
                      'previous': previous,
                      'next': next,
                      }
        hide_current = 0
        if self.current_uid == self.root_uid:
            parent_uid = None
            parent = None
        else:
            parent_uid = self._getParentUid(self.current_uid)
            parent = self._getObject(parent_uid)
        if not self.include_root and self.current_uid == self.root_uid:
            hide_current = 1

        if self.search or self.request_form.get('search'):
            parent_uid = parent = None
            hide_current = 1

        listing_info = {'current': self.current,
                        'current_uid': self.current_uid,
                        'parent': parent,
                        'parent_uid': parent_uid,
                        'hide_current': hide_current}

        chrono_stop = time()
        LOG('BaseNavigation.getListing', DEBUG, 'end\n'
            '\ttime elapsed %7.3fs\n' % (
             chrono_stop - chrono_start))

        return res, listing_info, batch_info

    def _searchItems(self):
        """Return current children if not in search mode."""
        if self.search or self.request_form.get('search'):
            return self._search()

        return self._getChildren(self.current, no_leaves=self.no_leaves,
                                 no_nodes=self.no_nodes, mode='listing')

    def _search(self):
        """Default search is done on uid in the current children.

        This method should be overriden in Navigation implementation."""
        res = self._getChildren(self.current, no_leaves=self.no_leaves,
                                no_nodes=self.no_nodes, mode='listing')
        q_uid = self.request_form.get('query_uid')
        LOG('BaseNavigation._search', DEBUG, 'searching %s' % q_uid)
        if q_uid:
            res = [r for r in res if self._getUid(r).find(q_uid) >= 0]

        return res

    def _filter(self, objs, mode='tree'):
        """Filter the objects according to init parameters.

        mode is either tree or listing,
        This method can be overriden in Navigation implementation."""
        return objs

    def _sort(self, objs, mode='tree'):
        """Sort objects according to init parameters.

        This method can be overriden in Navigation implementation."""
        return objs

    def _strNode(self, node, show_obj=1):
        text = ''
        lines = node['lines']
        for l in lines:
            if l == 0:
                text += '    '
            elif l == 1:
                text += '    |'
            elif l == 2:
                text += '    `'

        if node['state'] == 'open':
            text += '-> '
        elif node['state'] == 'closed':
            text += '-+ '
        else:
            text += '-- '
        if node.get('is_current'):
            text += '[%s]' % node['uid']
        else:
            text += node['uid']

        if show_obj:
            text += ": %s" % str(node['object'])

        # text += " - %d %s\n" % (node['level'], str(node['lines']))
        return text + '\n'

    def _strTree(self, tree, show_obj=1):
        """Dump a tree structure returned by a getTree into text."""
        text = '\n'
        for node in tree:
            text  += self._strNode(node, show_obj)
        return text

    # dumping
    def _exploreNodeForDump(self, obj, level, dump):
        if not obj:
            return
        obj_uid = self._getUid(obj)
        node = {'object': obj, 'level': level}
        children = self._getChildren(obj, no_leaves=1, mode='tree')
        children = filter(None, children)
        children = self._filter(children, mode='tree')
        children = self._sort(children, mode='tree')

        node['children_uids'] = [self._getUid(child) for child in children]
        dump[1][obj_uid] = node
        dump[0].append(obj_uid)
        for child in children:
            self._exploreNodeForDump(child, level+1, dump)

    def dumpTree(self):
        """Return a structure that can be easily processed to create a dump."""
        dump = ([], {})
        self._exploreNodeForDump(self.root, 0, dump)
        return dump
