##parameters=node, REQUEST
# $Id$
"""return a list of png representing the tree lines."""
# XXXX TODO i18n and l10n
# XXXX Move this function into non restricted code
from ZTUtils import make_query
from cgi import escape

# image are combination of line and state
# like tree_lm for corner minus
img = {0: 'tree_b',                     # blank
       1: 'tree_i',                     # vertical bar like I
       2: 'tree_l',                     # corner like a L
       'open': 'm',                     # minus
       'closed': 'p',                   # plus
       'node': 'n',                     # leaf node
       None: 'tree_r',                  # root
       }

lines = node['lines']

imgs = [img[x] for x in lines]
if not imgs:
    # roots
    imgs = [img[None]]
else:
    # shift
    imgs.insert(0, img[0])
state = node['state']

imgs[-1] = imgs[-1] + img[state]

img_src = '<img src="%s%%s.png" alt="" border="0" height="23" width="19" />'
img_src = img_src % context.portal_url.getBaseUrl()
imgs = [img_src % x for x in imgs]

if state in ('closed', 'open'):
    # add link to open/close node
    if state == 'closed':
        current_uid = node['uid']
        title = 'Déplier'
    else:
        current_uid = node['parent_uid']
        title = 'Plier'
    link = '%s?%s#entity_selected'%(REQUEST['URL0'],
                                    make_query(REQUEST.form,
                                               current_uid=current_uid,
                                               expand_all_from_current_uid=0))
    imgs[-1] = '<a href="%s" title="%s">%s</a>' % (escape(link), title, imgs[-1])
    if state == 'closed': # and node['level'] > 0:
        link = '%s?%s#entity_selected' % (
            REQUEST['URL0'], make_query(REQUEST.form,
                                        current_uid=current_uid,
                                        expand_all_from_current_uid=1))
        img = img_src % 'tree_expand'
        imgs[-1] = imgs[-1] + '<a href="%s" title="Déplier tout">%s</a>' % (escape(link), img)
return ''.join(imgs)
