##parameters=REQUEST, SESSION_KEY='CATALOGNAVIGATION'
# $Id$
from Products.CPSNavigation.CatalogNavigation import CatalogNavigation

TREE_PREF_SESSION_KEY = '%s_TREE_PREF' % SESSION_KEY
SEARCH_PREF_SESSION_KEY = '%s_SEARCH_PREF' % SESSION_KEY
OPTION_PREF_SESSION_KEY = '%s_OPTION_PREF'% SESSION_KEY

res = {'display_mode': 'tree',
       'current_uid': None,
       'tree': None,
       'listing': None,
       'listing_batch': None,
       'listing_batch_info': None,
       'rendered_search_form': '',
       'rendered_option_form': '',
       'status_form': '',
       'title': '',
       }

# manage form action
form = REQUEST.form
ltool = context.portal_layouts

if form.has_key('option_submit'):
    option_form = form
else:
    option_form = {}
if form.has_key('search_submit'):
    search_form = form
else:
    search_form = {}
if form.get('option_reset'):
    try:
        del REQUEST.SESSION[OPTION_PREF_SESSION_KEY]
        del REQUEST.SESSION[TREE_PREF_SESSION_KEY]['current_uid']
    except KeyError:
        pass
if form.get('search_reset'):
    try:
        del REQUEST.SESSION[SEARCH_PREF_SESSION_KEY]
    except KeyError:
        pass

# load pref from session
tree_pref = REQUEST.SESSION.get(TREE_PREF_SESSION_KEY, {})
search_pref = REQUEST.SESSION.get(SEARCH_PREF_SESSION_KEY, {})
option_pref = REQUEST.SESSION.get(OPTION_PREF_SESSION_KEY, {})

# process navigation option
save_tree_pref = 0
prefs = ('widget_id', 'layout_id', 'input_id',
         'current_uid', 'display_mode')
for pref in prefs:
    if form.has_key(pref):
        tree_pref[pref] = form.get(pref)
        save_tree_pref = 1
if save_tree_pref:
    REQUEST.SESSION[TREE_PREF_SESSION_KEY] = tree_pref
input_id = tree_pref.get('input_id')
widget_id = tree_pref.get('widget_id')
layout_id = tree_pref.get('layout_id')
current_uid = tree_pref.get('current_uid')
display_mode = tree_pref.get('display_mode')

# get the widget
widget = ltool[layout_id][widget_id]

if not widget.is_editable_option and display_mode == 'option':
    display_mode = None # prevent option edition
res['title'] = widget.popup_title
res['description'] = widget.popup_description
res['view_macro_path'] = widget.view_macro_path
res['popup_view_macro_path'] = widget.popup_view_macro_path
res['is_editable_option'] = widget.is_editable_option
res['input_id'] = input_id

# process option form
if not option_pref or display_mode == 'option':
    (res['rendered_option_form'], status, ds) = ltool.renderLayout(
        layout_id=widget.layout_option, schema_id=widget.schema_option,
        context=context, mapping=option_form, ob=option_pref)
    res['status_form'] = status
    if status != 'invalid':
        REQUEST.SESSION.set(OPTION_PREF_SESSION_KEY, option_pref)

# use current_uid and display_mode from option if not already set
if not current_uid:
    current_uid = option_pref.get('current_uid')
if not display_mode:
    display_mode = option_pref.get('display_mode')
res['current_uid'] = current_uid
res['display_mode'] = display_mode

if display_mode == 'option':
    return res

# process search form
if display_mode == 'search':
    (res['rendered_search_form'], status, ds) = ltool.renderLayout(
        layout_id=widget.layout_search, schema_id=widget.schema_search,
        context=context, mapping=search_form, ob=search_pref)
    res['status_form'] = status
    if status != 'invalid':
        REQUEST.SESSION.set(SEARCH_PREF_SESSION_KEY, search_pref)

# build nav options
kw = option_pref.copy()
#kw['root_uid'] = 'workspaces'

kw.update({'display_mode': display_mode,
           'current_uid': current_uid,
           'context': context,
           'request_form': form})

# build query
if display_mode == 'search':
    kw['search'] = 1
    if res['status_form'] == 'valid':
        query = search_pref.copy()
        if not query['scope']:
            query['folder_prefix'] = kw['current_uid']
        del query['scope']
        kw['query'] = query

# nav process init
nav = CatalogNavigation(**kw)
if display_mode == 'tree':
    res['tree'] = nav.getTree()

(res['listing'], res['listing_info'],
 res['listing_batch_info']) = nav.getListing()

return res
