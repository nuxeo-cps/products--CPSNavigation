##parameters=text, size=30
# $Id$

if text is None or len(text) < size:
    return text

mid_size = (size-3)/2
return text[:mid_size] + '...' + text[-mid_size:]
