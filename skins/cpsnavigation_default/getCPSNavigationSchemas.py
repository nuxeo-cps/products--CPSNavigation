##parameters=
# $Id$
"""Return schemas."""

navigation_option_schema = {
    'current_uid': {'type': 'CPS String Field', 'data': {}},
    'include_root': {'type': 'CPS Int Field',
                     'data': {'default_expr': 'python:1',}},
    'no_nodes': {'type': 'CPS Int Field',
                 'data': {'default_expr': 'python:0',}},
    'filter_tree_ptypes': {'type': 'CPS String List Field', 'data': {}},
    'filter_listing_ptypes': {'type': 'CPS String List Field', 'data': {}},
    'sort_tree_by': {'type': 'CPS String Field', 'data': {}},
    'sort_tree_direction': {'type': 'CPS String Field', 'data': {}},
    'sort_listing_by': {'type': 'CPS String Field', 'data': {}},
    'sort_listing_direction': {'type': 'CPS String Field', 'data': {}},
    'batch_size': {'type': 'CPS Int Field',
                   'data': {'default_expr': 'python:10',}},
    'display_mode': {'type': 'CPS String Field',
                     'data': {'default_expr': 'string:tree',}},
    'expand_all': {'type': 'CPS Int Field',
                     'data': {'default_expr': 'python:0',}},
    }

navigation_search_schema = {
    #search
    'SearchableText': {'type': 'CPS String Field', 'data': {}},
    'Title': {'type': 'CPS String Field', 'data': {}},
#    'Description': {'type': 'CPS String Field', 'data': {}},
    'Subject': {'type': 'CPS String List Field', 'data': {}},
    'Creator': {'type': 'CPS String Field', 'data': {}},
    'modified': {'type': 'CPS String Field', 'data': {}},
    'modified_usage': {'type': 'CPS String Field',
                       'data': {'default_expr': 'string:range:min'}},
    'scope': {'type': 'CPS Int Field',
              'data': {'default_expr': 'python:0',}},
    }

return {
    'navigation_search': navigation_search_schema,
    'navigation_option': navigation_option_schema,
    }
