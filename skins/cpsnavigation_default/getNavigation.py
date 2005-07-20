##parameters=finder, root_uid, prefix=None, filter_tree_ptypes=None, filter_listing_ptypes=None, REQUEST=None, batch_size=15
# $Id$
from Products.CPSNavigation.ConfNavigation import ConfNavigation
from Products.CPSNavigation.ZODBNavigation import ZODBNavigation
from Products.CPSNavigation.CPSNavigation import CPSNavigation
from Products.CPSNavigation.LDAPDirectoryNavigation import \
     LDAPDirectoryNavigation
from Products.CPSNavigation.CPSDirectoryNavigation import \
     CPSDirectoryNavigation
from Products.CPSNavigation.CPSIndirectDirectoryNavigation import \
     CPSIndirectDirectoryNavigation


type = finder
if finder == 'cps':
    current_uid = REQUEST.get('current_uid')
    if not current_uid:
        current_uid = root_uid
    # current_uid = context.portal_url.getRelativeContentURL(context)
    nav = CPSNavigation(root_uid=root_uid,
                        current_uid=current_uid,
                        prefix=prefix,
                        context=context,
                        include_root=1,
                        no_leaves=1,
                        filter_tree_ptypes=filter_tree_ptypes,
                        filter_listing_ptypes=filter_listing_ptypes,
                        sort_listing_by='title',
                        sort_listing_direction='asc',
                        batch_size=batch_size,
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
                         batch_size=batch_size,
                         request_form=REQUEST.form,
                         )
elif finder == 'cpsdirectory':
    current_uid = REQUEST.get('current_uid')
    dir_name = REQUEST.get('dir_name')
    if not dir_name:
        dir_name = root_uid
    dir = getattr(context.portal_directories, dir_name)
    indirect = 0
    if dir.meta_type == 'CPS Indirect Directory':
        indirect = 1
    elif dir.meta_type == 'CPS Local Directory':
        if dir.directory_type == 'CPS Indirect Directory':
            indirect = 1
    if dir.meta_type == 'CPS LDAP Directory':
        type = 'ldap'
        include_root = 1
        if not root_uid.endswith(','+dir.ldap_base):
            root_uid = dir.ldap_base
            include_root = 0
        if not current_uid:
            current_uid = REQUEST.get('current_uid', root_uid)
        nav = LDAPDirectoryNavigation(
            root_uid=root_uid,
            current_uid=current_uid,
            context=context,
            dir_name=dir_name,
            include_root=include_root,
            batch_size=batch_size,
            request_form=REQUEST.form,
            )
    elif indirect:
        type = 'map'
        nav = CPSIndirectDirectoryNavigation(
            root_uid=dir_name,
            current_uid=dir_name,
            context=context,
            dir_name=dir_name,
            include_root=0,
            batch_size=batch_size,
            request_form=REQUEST.form,
            )
    else:
        type = 'map'
        if root_uid and root_uid != dir_name:
            include_root = 1
        else:
            include_root = 0
        nav = CPSDirectoryNavigation(
            root_uid=root_uid,
            current_uid=current_uid,
            context=context,
            dir_name=dir_name,
            include_root=include_root,
            batch_size=batch_size,
            request_form=REQUEST.form,
            debug=1,
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
return tree, listing, batch_info, listing_info, type
