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
"""A ConfigParser Finder
"""
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from Products.CPSDefault.interfaces.Finder import Finder
from StringIO import StringIO


class DummyClass:
    """Look like a real class."""
    def __init__(self, id, **kw):
        self.id = id
        setattr(self, '_my_dummy_attr', kw.keys())
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        text = '<dummy id="%s"' % self.id
        if self._my_dummy_attr:
            for attr in self._my_dummy_attr:
                text += ' %s="%s"' % (attr, getattr(self, attr))

        return text + '>'

    def __cmp__(self, other):
        try:
            other_id = other.getId()
        except AttributeError:
            other_id = None
        return cmp(self.getId(), other_id)

    def getId(self):
        return self.id


class ConfFinder:
    """Implement Finder interface for a Conf/Ini file.

    example of conf file is:
    [root]
    contents=foo|bar|pom
    [foo]
    contents=bla|blah
    ...
    """
    __implements__ = (Finder, )     # See Finder interface for method docstring

    sep = '|'

    def __init__(self, file_name=None, file_content=None):
        """Initialize the Finder.

        Either a filename or a file content is expected."""
        if file_name:
            file_fd = open(file_name, 'r')
        elif text:
            file_fd = StringIO(text_conf)

        parser = ConfigParser()
        parser.readfp(file_fd)
        file_fd.close()
        self.parser = parser


    ### Finder interface
    def setParams(self, **kw):
        self._param_ids = kw.keys()
        for k, v in kw.items():
            setattr(self, k, v)

    def isNode(self, obj):
        if getattr(obj, 'type', '') in ('Section', 'Workspace'):
            return 1
        try:
            value = self.parser.get(obj.getId(), 'contents')
        except (NoSectionError, NoOptionError):
            return 0

        return 1

    def hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self.getChildren(obj, no_nodes, no_leaves))

    def getChildren(self, obj, no_nodes=0, no_leaves=0):
        children = []
        try:
            value = self.parser.get(obj.getId(), 'contents')
        except (NoSectionError, NoOptionError):
            return children
        children = [child.strip() for child in value.split(self.sep)]
        children = filter(None, children)
        children = [self._dummyfy(child) for child in children]
        if no_leaves:
            children = [child for child in children if self.isNode(child)]
        if no_nodes:
            children = [child for child in children if not self.isNode(child)]

        return children

    def getParents(self, obj):
        res = []
        parent = obj
        while parent:
            parent = self._findParent(parent)
            if parent:
                res.append(parent)

        return res


    ### Private
    def _dummyfy(self, id):
        """Turn an id into a Dummy object with properties."""
        # find a section
        kw = {}
        if id in self.parser.sections():
            options = self.parser.options(id)
            for option in options:
                if option not in ('id',):
                    kw[option] = self.parser.get(id, option)
        return DummyClass(id=id, **kw)

    def _findParent(self, obj):
        """find the parent of obj."""
        sections = self.parser.sections()
        for section in sections:
            for child in self.getChildren(DummyClass(section), no_leaves=0):
                if child == obj:
                    return self._dummyfy(section)
        if obj.getId() not in sections:
            raise KeyError
        return None


