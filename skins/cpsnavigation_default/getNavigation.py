##parameters=finder, root_uid, REQUEST=None
# $Id$
from Products.CPSNavigation.ConfNavigation import ConfNavigation
from Products.CPSNavigation.ZODBNavigation import ZODBNavigation
from Products.CPSNavigation.CPSNavigation import CPSNavigation
from Products.CPSNavigation.LDAPDirectoryNavigation import \
     LDAPDirectoryNavigation


if finder == 'cps':
    current_uid = REQUEST.get('current_uid')
    if not current_uid:
        current_uid = root_uid
    # current_uid = context.portal_url.getRelativeContentURL(context)
    nav = CPSNavigation(root_uid=root_uid,
                        current_uid=current_uid,
                        context=context,
                        include_root=1,
                        no_leaves=1,
                        # filter_tree_ptypes=('Workspace',),
                        # filter_listing_ptypes=('Link',),
                        sort_listing_by='title',
                        sort_listing_direction='asc',
                        batch_size=15,
                        request_form=REQUEST.form,
                        )
    # XXX try to get another tree and concatenate ?

elif finder == 'zodb':
    nav = ZODBNavigation(root=context.portal_url.getPortalObject(), #.sections,
                         current=context,
                         context=context,
                         # include_root=0,
                         # no_nodes=1,
                         # filter_tree_ptypes=('Workspace',),
                         # filter_listing_ptypes=('Link',),
                         sort_tree_by='date',
                         sort_tree_direction='asc',
                         sort_listing_by='title',
                         sort_listing_direction='desc',
                         batch_size=5,
                         request_form=REQUEST.form,
                         )
elif finder == 'ldap':
    current_uid = REQUEST.get('current_uid')
    dir_name = root_uid
    dir = getattr(context.portal_directories, dir_name)
    root_uid = dir.ldap_base
    if not current_uid:
        current_uid = root_uid
    current_uid = REQUEST.get('current_uid', root_uid)
    nav = LDAPDirectoryNavigation(
        root_uid=root_uid,
        current_uid=current_uid,
        context=context,
        dir_name=dir_name,
        include_root=0,
        batch_size=15,
        request_form=REQUEST.form,
        )

elif finder == 'conf':
    file_content = """
[root]
contents=node_1|node_2|leaf_1
[node_1]
contents=node_3|leaf_2
[node_2]
contents=leaf_3
[node_3]
contents=leaf_4|leaf_5
"""
    nav = ConfNavigation(root_uid='root',
                         current_uid='node_2',
                         file_content=file_content)

tree = None
if not REQUEST.get('search'):
    tree = nav.getTree()
listing, listing_info, batch_info = nav.getListing()
return tree, listing, batch_info, listing_info
