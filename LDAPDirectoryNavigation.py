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
"""A LDAPBackingDirectory Navigation
"""
import logging
import ldap
from Products.CMFCore.utils import getToolByName
from Products.CPSUtil.text import get_final_encoding
from BaseNavigation import BaseNavigation
from interfaces.IFinder import IFinder

logger = logging.getLogger(__name__)

class LDAPDirectoryNavigation(BaseNavigation):
    """Implement Finder interface for a LDAPDirectory."""
    __implements__ = (IFinder, )   # See IFinder interface for method docstring

    def toUtf8(self, s):
        if not isinstance(s, unicode):
            s = unicode(s, get_final_encoding(self._dir))
        return s.encode('utf8')

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

    @classmethod
    def asDict(self, resitem):
        """Transform a result item into a dict with dn."""
        d = resitem[1].copy()
        d['dn'] = resitem[0]
        return d

    ### Finder interface
    def _getObject(self, uid):
        # return an mapping of a directory entry
        if not isinstance(uid, unicode):
            enc = get_final_encoding(self._dir)
            uid = unicode(uid, enc)

        uid_utf8 = uid.encode('utf8')
        try:
            res = self._dir.searchLDAP(base=uid_utf8,
                                       scope=0,
                                       filter='(objectClass=*)',
                                       attrs=self._ldap_attrs)
        except ldap.LDAPError:
            logger.exception('_getObject: Error searching for dn=%r', uid_utf8)

        if not res:
            return None
        return self.asDict(res[0])


    def _getUid(self, obj):
        # return something like
        # 'ou=direction des musees de france,ou=culture,o=gouv,c=fr
        return obj['dn']

    def _isNode(self, obj):
        return 1

    def _hasChildren(self, obj, no_nodes=0, no_leaves=0):
        uid_utf8 = self.toUtf8(self._getUid(obj))
        try:
            res = self.dir.searchLDAP.search(base=uid_utf8,
                                         scope=1,
                                         filter=self._dir.objectClassFilter(),
                                         attrs=['dn'])
        except ldap.LDAPError:
            logger.exception(
                '_hasChildren: Error searching for dn=%r', uid_utf8)
            return False

        return bool(res)

    def _getChildren(self, obj, no_nodes=0, no_leaves=0, mode='tree'):
        uid = self._getUid(obj)
        uid_utf8 = self.toUtf8(uid)
        try:
            res = self._dir._delegate.search(
                base=uid_utf8,
                scope=1,
                filter=self._dir.objectClassFilter(),
                attrs=self._ldap_attrs)

        except ldap.LDAPError:
            logger.exception(
                '_hasChildren: Error searching for dn=%r', uid_utf8)
            return []

        children = [self.asDict(r) for r in res]
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

        base_utf8 = self.toUtf8(self._dir.ldap_base)
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

        logger.debug('_search: filter=%s attrs=%s', filter, self._ldap_attrs)

        try:
            res = self._dir.searchLDAP(base=base_utf8,
                                       scope=2,
                                       filter=filter,
                                       attrs=self._ldap_attrs)

        except ldap.LDAPError:
            logger.exception(
                '_search: Error searching filter=%s attrs=%s;', filter,
                self._ldap_attrs)
            return []

        return [self.asDict(r) for r in res]
