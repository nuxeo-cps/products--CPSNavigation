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

class Navigation:
    """
    """
    no_leaves = 0
    no_nodes = 0

    def __init__(self, finder, **kw):
        self._finder = finder
        self.setParams(**kw)
        self._finder.setParams(**kw)

    def setParams(self, **kw):
        """Setting navigation properties.

        main kw
        current : the current object
        node_only : listing only contains node (no leaf)
        """
        self._param_ids = kw.keys()
        for k, v in kw.items():
            setattr(self, k, v)

    def getParams(self):
        """Return the navigation properties."""
        res = {}
        for k in self._param_ids:
            res[k] = getattr(self, k)
        return res


    def exploreNode(self, obj, level, is_last_child, path, flat_tree):
        obj_id = obj.getId()
        node = {'id': obj_id,
                'object': obj,
                'level': level,
                'is_current': obj == self.current,
                'is_last_child': is_last_child,
                }
        if obj_id not in path:
            if self._finder.isNode(obj) and \
               self._finder.hasChildren(obj, no_leaves=1):
                node['has_children'] = 1
            else:
                node['has_children'] = 0
            flat_tree.append(node)
        else:
            children = self._finder.getChildren(obj, no_leaves=1)
            node['is_open'] = 1
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
                self.exploreNode(child, level+1, is_last_child,
                                 path, flat_tree)

    def getTree(self):
        """Return a flat Tree structure easily processed in ZPT."""
        # compute the path to current
        items = self._finder.getParents(self.current)
        items.reverse()
        items.append(self.current)
        path = [item.getId() for item in items]

        # explore tree using path
        tree = []
        self.exploreNode(items[0], 0, 0, path, tree)

        # compute vertical lines
        lines = []
        lv = lv_ = 0
        for node in tree:
            lv = node['level']
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
            if is_last_child:
                lines[-1] = 0
            lv_ = lv
            if node.get('is_open'):
                node['state'] = 'open'
            elif node.get('has_children'):
                node['state'] = 'closed'
            else:
                node['state'] = 'node'

        return tree

    def getListing(self):
        """Return a Listing structure."""
        res = self._finder.getChildren(self.current, no_leaves=self.no_leaves,
                                       no_nodes=self.no_nodes)
        return res


    def strNode(self, node, show_obj=1):
        text = ''
        lines = node['lines']
        for l in lines:
            if l == 0:
                text += '    '
            elif l == 1:
                text += '    |'
            elif l == 2:
                text += '    `'
        if node.get('is_open'):
            text += '-> '
        elif node.get('has_children'):
            text += '-+ '
        else:
            text += '-- '
        if node.get('is_current'):
            text += '[%s]' % node['id']
        else:
            text += node['id']

        if show_obj:
            text += ": %s" % str(node['object'])

#        text += " - %d %s\n" % (node['level'], str(node['lines']))
        return text + '\n'

    def strTree(self, tree, show_obj=1):
        """Dump a tree structure returned by a getTree into text."""
        text = '\n'
        for node in tree:
            text  += self.strNode(node, show_obj)
        return text
