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
"""Catalog Navigation widget types.
"""

from zLOG import LOG, DEBUG, TRACE
from Globals import InitializeClass

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType
from Products.CPSSchemas.BasicWidgets import CPSStringWidget, CPSStringWidgetType
from Products.CPSSchemas.BasicWidgets import renderHtmlTag, _isinstance

##################################################

class CatalogNavigationSelectWidget(CPSStringWidget):
    """This enable to peek a cps zodb object in edit mode using
    a catalog nav popup and display it as a link.in view mode."""
    meta_type = "CPS Catalog Navigation Select Widget"

    _properties = CPSStringWidget._properties + (
        {'id': 'popup_title', 'type': 'string', 'mode': 'w',
         'label': 'Title of the popup'},
        {'id': 'popup_description', 'type': 'string', 'mode': 'w',
         'label': 'A description of the popup'},
        {'id': 'view_macro_path', 'type': 'string', 'mode': 'w',
         'label': 'macro to display an item in the document'},
        {'id': 'popup_view_macro_path', 'type': 'string', 'mode': 'w',
         'label': 'macro to display an item in the popup window'},
        {'id': 'layout_search', 'type': 'string', 'mode': 'w',
         'label': 'Layout for searching'},
        {'id': 'schema_search', 'type': 'string', 'mode': 'w',
         'label': 'Schema for searching'},
        {'id': 'layout_option', 'type': 'string', 'mode': 'w',
         'label': 'Layout for configuration options'},
        {'id': 'schema_option', 'type': 'string', 'mode': 'w',
         'label': 'Schema for configuration options'},
        {'id': 'is_editable_option', 'type': 'boolean', 'mode': 'w',
         'label': 'Enable to edit option'},

        )
    popup_title = 'Catalog Navigation Popup'
    popup_description = 'a popup description'
    view_macro_path = 'here/catalognavigation_lib/macros/item_view'
    popup_view_macro_path = 'here/catalognavigation_lib/macros/popup_item_view'
    layout_search = 'navigation_search'
    schema_search = 'navigation_search'
    layout_option = 'navigation_option'
    schema_option = 'navigation_option'
    is_editable_option = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        datastructure[self.getWidgetId()] = value

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_catalognavigationselect_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        value = datastructure[self.getWidgetId()]
        obj = None
        if value:
            obj = self.restrictedTraverse(value)
        return meth(mode=mode, value=value, obj=obj)

InitializeClass(CatalogNavigationSelectWidget)


class CatalogNavigationSelectWidgetType(CPSStringWidgetType):
    """CatlogNavigationSelectwidget type."""
    meta_type = "CPS Catalog Navigation Select Widget Type"
    cls = CatalogNavigationSelectWidget

InitializeClass(CatalogNavigationSelectWidgetType)

##################################################

class CatalogNavigationMultiSelectWidget(CPSWidget):
    """ """
    meta_type = "CPS Catalog Navigation MultiSelect Widget"


InitializeClass(CatalogNavigationMultiSelectWidget)


class CatalogNavigationMultiSelectWidgetType(CPSWidgetType):
    """ """
    meta_type = "CPS Catalog Navigation MultiSelect Widget Type"
    cls = CatalogNavigationMultiSelectWidget

InitializeClass(CatalogNavigationMultiSelectWidgetType)

##################################################

WidgetTypeRegistry.register(CatalogNavigationSelectWidgetType,
                            CatalogNavigationSelectWidget)

# XXX: not yet impl
#WidgetTypeRegistry.register(CatalogNavigationMultiSelectWidgetType,
#                            CatalogNavigationMultiSelectWidget)
