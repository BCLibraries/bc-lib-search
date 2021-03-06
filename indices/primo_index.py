primo_index_request_body = {
    'alias': 'catalog',
    'settings': {
        'number_of_shards': 8,
        'number_of_replicas': 0,
        'refresh_interval': '-1'
    },
    'mappings': {
        'record': {
            '_all': {'enabled': true},
            'properties': {
                'title': {
                    'type': 'string'
                },
                'authors': {
                    'type': 'string'
                },
                'collections': {
                    'type': 'string',
                    'index': 'not_analzyed'
                },
                'subjects': {
                    'type': 'string'
                },
                'publisher': {
                    'type': 'string'
                },
                'location': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'oclc': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'language': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'series': {
                    'type': 'string'
                },
                'callnum': {
                    'type': 'string',
                    'fields': {
                        'display': {
                            'type': 'string',
                            'index': 'no'
                        }
                    }
                },
                'issn': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'isbn': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'notes': {
                    'type': 'string'
                },
                'toc': {
                    'type': 'string'
                },
                'alttitles': {
                    'type': 'string'
                },
                'tax1': {
                    'type': 'string',
                    'index': 'not_analyzed',
                    'include_in_all': false
                },
                'tax2': {
                    'type': 'string',
                    'index': 'not_analyzed',
                    'include_in_all': false
                },
                'tax3': {
                    'type': 'string',
                    'index': 'not_analyzed',
                    'include_in_all': false
                }
            }
        }
    }
}
