##parameters=
#$Id$
"""
Here are defined the vocabularies.
"""

vocabularies = {
    'navigation_sort_tree_by': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('', "choose"),
                            ('date', "Date"),
                            ('review_state', "Review State"),)
                 },
        },
    'navigation_sort_listing_by': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('', "choose"),
                            ('date', "Date"),
                            ('review_state', "Review State"),)
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
