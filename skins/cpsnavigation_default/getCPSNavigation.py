##parameters=REQUEST, SESSION_KEY='CPSNAVIGATION'
# $Id$
from Products.CPSNavigation.CPSNavigation import CPSNavigation

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
       }

# manage form action
form = REQUEST.form
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
if form.has_key('current_uid'):
    tree_pref['current_uid'] = form.get('current_uid')
    save_tree_pref = 1
if form.has_key('display_mode'):
    tree_pref['display_mode'] = form.get('display_mode')
    save_tree_pref = 1
if save_tree_pref:
    REQUEST.SESSION[TREE_PREF_SESSION_KEY] = tree_pref
current_uid = tree_pref.get('current_uid')
display_mode = tree_pref.get('display_mode')

ltool = context.portal_layouts
# process option form
if not option_pref or display_mode == 'option':
    (res['rendered_option_form'], status, ds) = ltool.renderLayout(
        layout_id='navigation_option', schema_id='navigation_option',
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
        layout_id='navigation_search', schema_id='navigation_search',
        context=context, mapping=search_form, ob=search_pref)
    res['status_form'] = status
    if status != 'invalid':
        REQUEST.SESSION.set(SEARCH_PREF_SESSION_KEY, search_pref)

# build nav options
kw = option_pref.copy()

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
nav = CPSNavigation(**kw)

if display_mode == 'tree':
    res['tree'] = nav.getTree()

(res['listing'], res['listing_info'],
 res['listing_batch_info']) = nav.getListing()

return res
