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
"""A LDAPDirectory Navigation
"""
from types import DictType
from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from interfaces.IFinder import IFinder
from BaseNavigation import BaseNavigation
from zLOG import LOG, DEBUG, ERROR
try:
    from Products.LDAPUserGroupsFolder.utils import filter_format
except ImportError:
   def filter_format(filter_template,assertion_values):
       # redefine an empty filter to be able to use CPSNavigation
       # without installing LDAPUserGroupFolder
       LOG('LDAPDirectoryNavigation filter_format', ERROR,
           "WARNING using fake function filter_format !"
           "you should install LDAPUserGroupsFolder.")
       return filter_template % (assertion_values)


class LDAPDirectoryNavigation(BaseNavigation):
    """Implement Finder interface for a LDAPDirectory."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    def __init__(self, **kw):
        if not kw.get('context'):
            raise KeyError, 'No context provided.'
        if not kw.get('dir_name'):
            raise KeyError, 'No dir_name provided.'

        self._dir = getToolByName(kw['context'],
                                  'portal_directories')[kw['dir_name']]
        self._ldap_attrs = self._getAttrs(kw['context'])
        BaseNavigation.__init__(self, **kw)


    def _getAttrs(self, context):
        # return list of ldap attributes
        attrs = [x['id'] for x in
                 context.getDirectoryResultFields(self._dir.getId(),
                                                  self._dir.title_field)]
        if 'dn' not in attrs:
            attrs.append('dn')
        if self._dir.title_field not in attrs:
            attrs.append(self._dir.title_field)
        return attrs

    ### Finder interface
    def _getObject(self, uid):
        # return an mapping of a directory entry
        uid_utf8 = unicode(uid, 'iso-8859-15').encode('utf8')
        res = self._dir._delegate.search(base=uid_utf8,
                                         scope=0,
                                         filter='(objectClass=*)',
                                         attrs=self._ldap_attrs)
        if res['exception']:
            LOG('LDAPDirectoryNavigation._getObject',
                ERROR, 'Error searching for dn=[%s]: %s' %
                (uid, res['exception']))
            return None
        if not res['size']:
            return None
        return res['results'][0]


    def _getUid(self, obj):
        # return something like
        # 'ou=direction des musees de france,ou=culture,o=gouv,c=fr
        # uid is encoded in iso 8859 15
        return obj['dn']

    def _isNode(self, obj):
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        uid = self._getUid(obj)
        uid_utf8 = unicode(uid, 'iso-8859-15').encode('utf8')
        res = self._dir._delegate.search(base=uid_utf8,
                                         scope=1,
                                         filter=self._dir.objectClassFilter(),
                                         attrs=['dn'])
        if res['exception']:
            LOG('LDAPDirectoryNavigation._hasChildren',
                ERROR, 'LDAP search error on dn=%s: %s' % (uid,
                                                           res['exception']))
            return 0

        return res['size']

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        uid = self._getUid(obj)
        uid_utf8 = unicode(uid, 'iso-8859-15').encode('utf8')
        res = self._dir._delegate.search(base=uid_utf8,
                                         scope=1,
                                         filter=self._dir.objectClassFilter(),
                                         attrs=self._ldap_attrs)
        if res['exception']:
            LOG('LDAPDirectoryNavigation._getChildren',
                ERROR, 'LDAP search error on dn=%s: %s' % (uid,
                                                           res['exception']))
            return []
        children = res['results']
        if no_nodes:
            children = [child for child in children if not self._isNode(child)]

        return children

    def _getParentUid(self, uid):
        parent_uid = uid.split(',', 1)[1]
        return parent_uid

    ### override Navigation
    def _search(self):
        """Default search is done on uid in the current children.

        This method should be overriden in Navigation implementation."""

        base_utf8 = unicode(self._dir.ldap_base, 'iso-8859-15').encode('utf8')
        key = self._ldap_attrs[0]
        query = self.request_form.get('query_uid', '').strip()
        filter = ''
        if not query:
            return []
        for attr in self._ldap_attrs:
            if attr == 'dn':
                continue
            if attr in self._dir.search_substring_fields:
                f = filter_format('(%s=*%s*)', (attr, query))
            else:
                f = filter_format('(%s=%s)', (attr, query))
            filter += f
        filter = '(&(objectClass=*)(|%s))' % filter

        if self.debug:
            LOG('LDAPDirectoryNavigation._search', DEBUG,
                'filter=%s attrs=%s' % (filter, self._ldap_attrs))

        res = self._dir._delegate.search(base=base_utf8,
                                         scope=2,
                                         filter=filter,
                                         attrs=self._ldap_attrs)
        if res['exception']:
            LOG('LDAPDirectoryNavigation._search',
                ERROR, 'Error searching filter=%s attrs=%s: %s' %
                (filter, self._ldap_attrs,  res['exception']))
            return []



        if not res['size']:
            return []
        return res['results']
