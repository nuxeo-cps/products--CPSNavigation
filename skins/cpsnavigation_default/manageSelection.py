##parameters=REQUEST, **kw
# $Id$
"""Manage selection and return current selection."""
if REQUEST is not None:
    kw.update(REQUEST.form)

def getMapFromUid(uid, type):
    if type == 'folder':
        obj = context.restrictedTraverse(uid)
        return {'uid': uid,
                'title_or_id': obj.title_or_id,
                'img_tag': context.getImgTag(obj.getIcon())}

type = kw.get('type', 'folder')
session_key = 'CPS_SELECTION_%s' % type
selection = REQUEST.SESSION.get(session_key, [])

if kw.has_key('del_items_from_selection'):
    uids = kw.get('selected_uids', [])
    selection = [s for s in selection if s not in uids]
    REQUEST.SESSION[session_key] = selection

if kw.has_key('add_items_to_selection'):
    uids = kw.get('uids', [])
    for uid in uids:
        if uid not in selection:
            selection.append(uid)
    REQUEST.SESSION[session_key] = selection

if kw.has_key('send_selection'):
    # send selection to windows opener
    pass

res = []
for s in selection:
    res.append(getMapFromUid(s, type))
return res

