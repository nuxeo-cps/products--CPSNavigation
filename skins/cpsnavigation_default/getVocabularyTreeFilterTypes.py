##parameters=key=None
#$Id$
"""
return the portal type vocabulary, used as MethodVocabulary
"""
def cmp_type(a, b):
    # Some types are favored so they show up at the top of the list
    if a.getId() in ('Workspace', 'Section'):
        return -1
    if b.getId() in ('Workspace', 'Section'):
        return 1
    aa = l10n(a.Title()).lower()
    bb = l10n(b.Title()).lower()
    return cmp(aa, bb)

def l10n(s):
    cpsmcat = context.Localizer.default
    ret = cpsmcat(s)
    if same_type(ret, u''):
        return ret.encode('iso-8859-15', 'ignore')
    else:
        return ret

ttool = context.portal_types
types = []
for ti in ttool.listTypeInfo():
    if hasattr(ti, 'cps_proxy_type') and ti.cps_proxy_type in (
        'folder', 'folderishdocument'):
        types.append(ti)
types.sort(cmp_type)

res = [(item.getId(), l10n(item.Title()))
       for item in types]

if key is not None:
    res = [item[1] for item in res if item[0] == key][0]

return res