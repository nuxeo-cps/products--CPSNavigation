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
"""A CPS Indirect Directory Navigation
"""

from zLOG import LOG, DEBUG, ERROR
from CPSDirectoryNavigation import CPSDirectoryNavigation

class CPSIndirectDirectoryNavigation(CPSDirectoryNavigation):
    """Navigation for CPS Indirect Directory.

    The only change compared to a navigation for CPS Directory is the search,
    that is not made within the references hold by the indirect directory, but
    within the possible entries it can possibly hold, e.g all the entries
    stored in all the directories the indirect directory can refer.
    """

    ### override Navigation
    def _search(self):
        key = self._dir.id_field
        query_pattern = self.request_form.get('query_uid', '').strip()
        if not query_pattern:
            return []
        query = {key:query_pattern}

        if self.debug:
            LOG('CPSIndirectDirectoryNavigation._search', DEBUG,
                'query=%s attrs=%s' % (query, self._attrs))

        # change is here: search is done by calling searchPossibleEntries
        # instead of searchEntries on the indirect directory
        res = self._dir.searchPossibleEntries(return_fields=self._attrs,
                                              **query)
        for r in res:
            r[1].update({'the_uid': r[0]})
        res = [r[1] for r in res]
        return res
