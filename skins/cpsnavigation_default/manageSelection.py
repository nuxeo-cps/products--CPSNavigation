##parameters=REQUEST, **kw
# $Id$
"""Manage selection and return current selection."""
if REQUEST is not None:
    kw.update(REQUEST.form)

def getMapFromUid(uid, type):
    if type == 'cps':
        obj = context.restrictedTraverse(uid)
        return {'uid': uid,
                'title_or_id': obj.title_or_id,
                'img_tag': context.getImgTag(obj.getIcon())}
    elif REQUEST.get('vocabulary'):
        title = uid
        vocabulary_name = REQUEST.get('vocabulary')
        vocabulary = getattr(context.portal_vocabularies, vocabulary_name)
        title = vocabulary.get(uid, uid)
        return {'uid': uid,
                'title': title}
    else:
        # XXX return default for map or ldap without vocabulary ?
        pass

type = kw.get('type', 'cps')
root_uid = kw.get('root_uid', 'sections')
session_key = 'CPS_SELECTION_%s_%s' % (type, root_uid)
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
