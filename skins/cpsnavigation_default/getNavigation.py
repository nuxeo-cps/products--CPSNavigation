##parameters=finder='zodb'
from Products.CPSNavigation.ZODBNavigation import ZODBNavigation
from Products.CPSNavigation.ConfNavigation import ConfNavigation

if finder == 'zodb':
    nav = ZODBNavigation(root=context.portal_url.getPortalObject(),
                         current=context)
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

tree = nav.getTree()
listing = nav.getListing()
return tree, listing


## a goal:
## nav = Navigation(root_uid=portal, current=context, include_root=0,
##                  filter = ('no_nodes', 'no_hidden', 'published')
##                  sort = ('state:asc', 'date:desc'),
##                  batch = {'size': 12, 'b_start':3},
##                            )

