##parameters=REQUEST=None
# $Id$
from Products.CPSNavigation.CPSNavigation import CPSNavigation

res = {'display_mode': 'tree',
       'tree': None,
       'listing': None,
       'listing_batch': None,
       'listing_batch_info': None,
       'rendered_search_form': '',
       'rendered_option_form': '',
       'status_form': '',
       }

ltool = context.portal_layouts
utool = context.portal_url
form = {}
if REQUEST:
    form = REQUEST.form

# process nav options form
res['rendered_option_form'], status_opt, ds_opt = ltool.renderLayout(
    layout_id='navigation_option',
    schema_id='navigation_option',
    context=context,
    mapping=form)

# process search form
res['rendered_search_form'], status_search, ds_search = ltool.renderLayout(
    layout_id='navigation_search',
    schema_id='navigation_search',
    context=context,
    mapping=form)

dm_opt = ds_opt.getDataModel()
dm_search = ds_search.getDataModel()

# build nav options
kw = {}
for key in dm_opt.keys():
    kw[key] = dm_opt[key]

if not kw['current_uid']:
    kw['current_uid'] = utool.getRelativeUrl(context)
kw.update({'root': utool.getPortalObject(),
           'context': context,
           'request_form': form})

display_mode = kw['display_mode']
res['display_mode'] = display_mode
if display_mode == 'options' and form.get('submit'):
    res['status_form'] = status_opt

if form.get('submit') and display_mode == 'search':
    # validate form
    kw['search'] = 1
    res['status_form'] = status_search
    if status_search == 'valid':
        query = {}
        for key in dm_search.keys():
            query[key] = dm_search[key]
        if not query['scope']:
            query['folder_prefix'] = kw['current_uid']
        del query['scope']
        kw['query'] = query

# nav process init
nav = CPSNavigation(**kw)

if display_mode == 'tree':
    res['tree'] = nav.getTree()

if display_mode == 'search' and not form.get('submit'):
    return res

(res['listing'], res['listing_info'],
 res['listing_batch_info']) = nav.getListing()

return res
