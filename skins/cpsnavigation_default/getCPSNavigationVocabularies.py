##parameters=
#$Id$
"""
Here are defined the vocabularies.
"""

vocabularies = {
    'navigation_sort_tree_by': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('', "choose"),
                            ('id', "Id"),
                            ('title', "Title"),)
                 },
        },
    'navigation_sort_listing_by': {
        'type': 'CPS Vocabulary',
        #XXX not i18n
        'data': {'tuples': (('', "choose"),
                            ('date', "Modified date"),
                            ('time', "Last workflow transition"),
                            ('review_state', "Review State"),
                            ('Title', "Title"),
                            ('Subject', "Subject"),
                            ('Creator', "Creator"),
                            ('portal_type', "Type"),)
                 },
        },
    'navigation_sort_direction': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('', "choose"),
                            ('asc', "Ascendant"),
                            ('desc', "Descendant")),
                 },
        },
    'navigation_filter_tree_ptypes': {
        'type': 'CPS Method Vocabulary',
        'data': {'get_vocabulary_method': 'getVocabularyTreeFilterTypes'
                 },
        },
    'navigation_filter_listing_ptypes': {
        'type': 'CPS Method Vocabulary',
        'data': {'get_vocabulary_method': 'getVocabularyListingFilterTypes'
                 },
        },
    'navigation_filter_review_state': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('work', "Work"),
                            ('pending', "Pending"),
                            ('published', "Published"),)
                 },
        },
    'navigation_display_mode': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('tree', "Navigation"),
                            ('search', "Search"),
                            ('options', "Options"),)
                 },
        },
    }

return vocabularies
