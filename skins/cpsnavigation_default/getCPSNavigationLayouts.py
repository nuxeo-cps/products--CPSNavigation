##parameters=
# $Id$
"""Return layouts types."""

navigation_search_layout = {
    'widgets': {
        'SearchableText': {
            'type': 'String Widget',
            'data': {
                'fields': ['SearchableText'],
                'is_i18n': 1,
                'label_edit': 'label_search_full_text',
                'display_width': 25,
                'size_max': 100,
                },
            },
        'Title': {
            'type': 'String Widget',
            'data': {
                'fields': ['Title'],
                'is_i18n': 1,
                'label_edit': 'label_title',
                'display_width': 25,
                'size_max': 250,
                },
            },
##         'Description': {
##             'type': 'String Widget',
##             'data': {
##                 'fields': ['Description'],
##                 'is_i18n': 1,
##                 'label_edit': 'label_description',
##                 'width': 20,
##                 'size_max': 100,
##                 },
##             },
        'Subject': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ['Subject'],
                'is_i18n': 1,
                'label_edit': 'label_subject',
                'vocabulary': 'subject_voc',
                'size': 3,
                },
            },
##         'Creator': {
##             'type': 'Directory Entry Widget',
##             'data': {
##                 'fields': ['Creator'],
##                 'is_i18n': 1,
##                 'label_edit': 'label_creator',
##                 'vocabulary': 'members',
##                 'directory': 'members',
##                 'entry_type': 'id',
##                 'popup_mode': 'search',
##                 },
##             },
        'modified': {
            'type': 'DateTime Widget',
            'data': {
                'fields': ['modified'],
                'is_i18n': 1,
                'label_edit': 'label_search_modified_since',
                'time_setting': 0,
                'time_hour_default': '00',
                'time_minutes_default': '00',
                },
            },
        'scope': {
           'type': 'Boolean Widget',
           'data': {
                'fields': ['scope'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_search_scope',
                'label_false': 'cpsnav_search_scope_current_location',
                'label_true': 'cpsnav_search_scope_entire_site',
                },
            },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'SearchableText'}, ],
                 [{'widget_id': 'Title'}, ],
                 [{'widget_id': 'Subject'}, ],
#                 [{'widget_id': 'Creator'}, ],
                 [{'widget_id': 'modified'}, ],
                 [{'widget_id': 'scope'}, ],
                 ],
        }
    }

navigation_option_layout = {
    'widgets': {
        'include_root': {
           'type': 'Boolean Widget',
           'data': {
                'fields': ['include_root'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_include_root',
                },
            },
        'current_uid': {
            'type': 'String Widget',
            'data': {
                'fields': ['current_uid'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_current_uid',
                'display_width': 72,
                'size_max': 255,
                },
            },
        'no_nodes': {
           'type': 'Boolean Widget',
           'data': {
                'fields': ['no_nodes'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_no_node',
                },
            },
        'batch_size': {
            'type': 'Int Widget',
            'data': {
                'fields': ['batch_size'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_batch_size',
                'is_limited': 1,
                'min_value': 1,
                'max_value': 100,
                'display_width': 4,
                },
            },
        'filter_tree_ptypes': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ['filter_tree_ptypes'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_filter_tree_ptypes',
                'vocabulary': 'navigation_filter_tree_ptypes',
                'size': 10,
                },
            },
        'filter_listing_ptypes': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ['filter_listing_ptypes'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_filter_listing_ptypes',
                'vocabulary': 'navigation_filter_listing_ptypes',
                'size': 10,
                },
            },
        'sort_tree_by': {
            'type': 'Select Widget',
            'data': {
                'fields': ['sort_tree_by'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_sort_tree_by',
                'vocabulary': 'navigation_sort_tree_by',
                },
            },
        'expand_all': {
           'type': 'Boolean Widget',
           'data': {
                'fields': ['expand_all'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_search_expand_all',
                },
            },
        'sort_listing_by': {
            'type': 'Select Widget',
            'data': {
                'fields': ['sort_listing_by'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_sort_listing_by',
                'vocabulary': 'navigation_sort_listing_by',
                },
            },
        'sort_listing_direction': {
            'type': 'Select Widget',
            'data': {
                'fields': ['sort_listing_direction'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_sort_listing_direction',
                'vocabulary': 'navigation_sort_direction',
                },
            },
        'sort_tree_direction': {
            'type': 'Select Widget',
            'data': {
                'fields': ['sort_tree_direction'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_sort_tree_direction',
                'vocabulary': 'navigation_sort_direction',
                },
            },
        'display_mode': {
            'type': 'Select Widget',
            'data': {
                'fields': ['display_mode'],
                'is_i18n': 1,
                'label_edit': 'cpsnav_option_display_mode',
                'vocabulary': 'navigation_display_mode',
                },
            },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'current_uid'}, ],
                 [{'widget_id': 'display_mode'}, ],
                 [{'widget_id': 'include_root'}, ],
                 [{'widget_id': 'sort_tree_by'},
                  {'widget_id': 'sort_tree_direction'}, ],
                 [{'widget_id': 'expand_all'}, ],
                 [{'widget_id': 'sort_listing_by'},
                  {'widget_id': 'sort_listing_direction'}, ],
                 [{'widget_id': 'batch_size'}, ],
                 [{'widget_id': 'no_nodes'}, ],
                 [{'widget_id': 'filter_tree_ptypes'},
                  {'widget_id': 'filter_listing_ptypes'}, ],
                 ],
        }
    }

return {'navigation_search': navigation_search_layout,
        'navigation_option': navigation_option_layout}
