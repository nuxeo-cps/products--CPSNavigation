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


class Finder(Interface):
    """
    General interface to implement a Finder.

    These methods need to be implemented by any class that wants to be
    used by Navigation.
    """

    def setParams(**kw):
        """Initialize the navigation parameters."""

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

    def getParents(obj):
        """Return a list of parents of obj from father to the root.

        If obj is not known this raise a KeyError.
        """
