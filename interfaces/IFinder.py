# (C) Copyright 2004 Nuxeo SAS <http://nuxeo.com>
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
""" Finder interface.
"""
from Interface import Interface


class IFinder(Interface):
    """
    General interface to implement a Finder.

    These methods need to be implemented by any class that wants to be
    used by Navigation.
    """

    def _getObject(uid):
        """Return the object corresponding to the unique identifier.

        Return None if uid not found.
        """

    def _getUid(obj):
        """Return the unique identifier.

        Return None if object not found.
        """

    def _isNode(obj):
        """True if obj is a node, 0 for a leaf.

        A node is container that may be empty,
        if obj is not know this raise a KeyError.
        """

    def _hasChildren(obj, no_nodes=0, no_leaves=0):
        """Return true if object has children.

        Use no_leaves=1 to know if obj has children nodes.
        """

    def _getChildren(obj, no_nodes=0, no_leaves=0, mode='tree'):
        """Return a list of children objects of obj.

        If obj is not known this raise a KeyError.
        If no children return [].
        """

    def _getParentUid(uid):
        """Return the parent uid of uid.

        If obj has no parent return None.
        """
