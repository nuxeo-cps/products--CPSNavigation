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
"""A ConfigParser Navigation
"""
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from StringIO import StringIO
from Products.CPSNavigation.interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation

class ConfNavigation(BaseNavigation):
    """Implement Finder interface for a Conf/Ini file.

    example of conf file is:
    [root]
    contents=foo|bar|pom
    [foo]
    contents=bla|blah
    ...
    """
    __implements__ = (IFinder, )  # See Finder interface for method docstring

    sep = '|'

    def __init__(self, **kw):
        """Initialize the Finder.

        Either a filename or a file content is expected."""
        file_fd = None
        if kw.get('file_name'):
            file_fd = open(kw['file_name'], 'r')
        elif kw.get('file_content'):
            file_fd = StringIO(kw['file_content'])
        else:
            raise KeyError, "No file_content or file_name provided."
        parser = ConfigParser()
        parser.readfp(file_fd)
        file_fd.close()
        self._parser = parser
        BaseNavigation.__init__(self, **kw)


    ### Finder interface
    def _getObject(self, uid):
        """Warning getObject always return an object even if uid is
        unknown."""
        return self._dummyfy(uid)

    def _getUid(self, obj):
        return obj.getId()

    def _isNode(self, obj):
        # support dump_tree export
        if getattr(obj, 'type', '') in ('Section', 'Workspace'):
            return 1
        try:
            self._parser.get(obj.getId(), 'contents')
        except (NoSectionError, NoOptionError):
            return 0

        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        # Such an ineficient way
        return not not len(self._getChildren(obj, no_nodes, no_leaves))

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        children = []
        try:
            value = self._parser.get(obj.getId(), 'contents')
        except (NoSectionError, NoOptionError):
            return children
        children = [child.strip() for child in value.split(self.sep)]
        children = filter(None, children)
        children = [self._dummyfy(child) for child in children]
        if no_leaves:
            children = [child for child in children if self._isNode(child)]
        if no_nodes:
            children = [child for child in children if not self._isNode(child)]

        return children

    def _getParentUid(self, uid):
        obj = self._getObject(uid)
        sections = self._parser.sections()
        for section in sections:
            for child in self._getChildren(DummyClass(section), no_leaves=0):
                if child == obj:
                    return section
        return None

    ### Private
    def _dummyfy(self, id):
        """Turn an id into a Dummy object with properties."""
        # find a section
        kw = {}
        if id in self._parser.sections():
            options = self._parser.options(id)
            for option in options:
                if option not in ('id',):
                    kw[option] = self._parser.get(id, option)
        return DummyClass(id=id, **kw)


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
