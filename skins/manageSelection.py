##parameters=REQUEST, **kw
# $Id$

if REQUEST is not None:
    kw.update(REQUEST.form)

def getMapFromUid(uid, type):
    if type == 'folder':
        obj = context.restrictedTraverse(uid)
        return {'uid': uid,
                'title_or_id': obj.title_or_id,
                'img_tag': context.getImgTag(obj.getIcon())}


mode = kw.get('mode')
type = kw.get('type', 'folder')
session_key = 'CPS_SELECTION_%s' % type
if mode == 'get':
    selection = REQUEST.SESSION.get(session_key, [])
    res = []
    for s in selection:
        res.append(getMapFromUid(s, type))
    return res

if kw.has_key('del_items_from_selection'):
    uids = kw.get('selected_uids', [])
    selection = REQUEST.SESSION.get(session_key, [])
    REQUEST.SESSION[session_key] = [s for s in selection if s not in uids]
    current_uid = kw.get('current_uid')
    REQUEST.RESPONSE.redirect(REQUEST.URL1 +
                              '/test_cps_navigation?current_uid=%s' %
                              current_uid)
    return

if kw.has_key('add_items_to_selection'):
    uids = kw.get('uids', [])
    selection = REQUEST.SESSION.get(session_key, [])
    for uid in uids:
        if uid not in selection:
            selection.append(uid)
    REQUEST.SESSION[session_key] = selection
    current_uid = kw.get('current_uid')
    REQUEST.RESPONSE.redirect(REQUEST.URL1 +
                              '/test_cps_navigation?current_uid=%s' %
                              current_uid)
    return

if kw.has_key('send_selection'):
    # send selection to windows opener
    pass
