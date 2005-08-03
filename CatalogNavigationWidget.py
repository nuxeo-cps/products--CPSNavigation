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

XXXX Warning this code use CatalogNavigation which is not uptodate with CPS
Core > 3.18.0. This means that it does not support i18n document.
"""

from zLOG import LOG, DEBUG, TRACE
from Globals import InitializeClass

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType
from Products.CPSSchemas.BasicWidgets import CPSURLWidget

##################################################

class CatalogNavigationSelectWidget(CPSURLWidget):
    """This enable to peek a cps zodb object in edit mode using
    a catalog nav popup and display it as a link.in view mode."""
    meta_type = "CPS Catalog Navigation Select Widget"

    _properties = CPSURLWidget._properties + (
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Widget render method'},
        {'id': 'popup_title', 'type': 'string', 'mode': 'w',
         'label': 'Popup title'},
        {'id': 'popup_description', 'type': 'string', 'mode': 'w',
         'label': 'Popup description'},
        {'id': 'layout_search', 'type': 'string', 'mode': 'w',
         'label': 'Layout for search'},
        {'id': 'schema_search', 'type': 'string', 'mode': 'w',
         'label': 'Schema for search'},
        {'id': 'is_editable_option', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow configuration options'},
        {'id': 'layout_option', 'type': 'string', 'mode': 'w',
         'label': 'Layout for configuration options'},
        {'id': 'schema_option', 'type': 'string', 'mode': 'w',
         'label': 'Schema for configuration options'},
        {'id': 'popup_view_macro_path', 'type': 'string', 'mode': 'w',
         'label': 'Macro to display an item in the popup'},
        {'id': 'popup_edit_macro_path', 'type': 'string', 'mode': 'w',
         'label': 'Macro to display an item in the document from the popup'},
        {'id': 'preprocess_method', 'type': 'string', 'mode': 'w',
         'label': 'Method to customize CatalogNavigation arguments'},
        )
    render_method = 'widget_catalognavigationselect_render'
    popup_title = ''
    popup_description = ''
    layout_search = 'navigation_search'
    schema_search = 'navigation_search'
    is_editable_option = 0
    layout_option = 'navigation_option'
    schema_option = 'navigation_option'
    popup_view_macro_path = 'here/catalognavigation_lib_popup_item_view/macros/popup_item_view'
    popup_edit_macro_path = 'here/catalognavigation_lib_popup_item_edit/macros/popup_item_edit'
    preprocess_method = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        datastructure[self.getWidgetId()] = value
        datastructure[self.getWidgetId() + '_set'] = ''

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        widget_set_id = widget_id + '_set'
        datamodel = datastructure.getDataModel()
        if not self.is_required and not datastructure[widget_set_id]:
            v = ''
        else:
            v = datastructure[widget_id]
        err, v = self._extractValue(v)
        if not err and v and not self.checkUrl(v):
            err = 'cpsschemas_err_url'
        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v
        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = self.render_method
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        value = datastructure[self.getWidgetId()]
        return meth(mode=mode, value=value)

InitializeClass(CatalogNavigationSelectWidget)


class CatalogNavigationSelectWidgetType(CPSWidgetType):
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
