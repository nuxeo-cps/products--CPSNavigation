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
""" Finder interface.
"""
from Interface import Interface


class IFinder(Interface):
    """
    General interface to implement a Finder.

    These methods need to be implemented by any class that wants to be
    used by Navigation.
    """

    def setParams(**kw):
        """Initialize the navigation parameters.

        This method should be called before using any others.
        You can assert to have kw['root'] with the root object."""

    def getObject(uid):
        """Return the object corresponding to the unique identifier.

        Return None if uid not found."""

    def getUid(obj):
        """Return the unique identifier."""

    def isNode(obj):
        """True if obj is a node, 0 for a leaf.

        A node is container that may be empty,
        if obj is not know this raise a KeyError."""

    def hasChildren(obj, no_nodes=0, no_leaves=0):
        """Return true if object has children.

        Use no_leaves=1 to know if obj has children nodes.
        """

    def getChildren(obj, no_nodes=0, no_leaves=0):
        """Return a list of children objects of obj.

        If obj is not known this raise a KeyError.
        """

    def getParent(obj):
        """Return the parent of obj.

        If obj has no parent return None.
        If obj is not known this raise a KeyError.
        """
