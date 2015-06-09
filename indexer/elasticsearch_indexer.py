from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging


class ElasticSearchIndexer(object):
    def __init__(self, host, bulk_size=1000):
        self.es = Elasticsearch([{'host': host}])
        self.actions = []
        self.logger = logging.getLogger(__name__)
        self.bulk_size = bulk_size

    def add(self, item):
        self._add_actions([{
            '_index': 'catalog',
            '_type': 'record',
            '_id': item['id'],
            '_source': item
        }])

    def update(self, data):
        pass

    def delete(self, id):
        pass

    def close(self):
        self._post()

    def add_autocomplete(self, text, type=None, weight=None):
        source = {
            'output': text,
            'input': [
                text
            ],
            'payload': {
                'term': text,
                'type': type
            },
            'weight': weight
        }
        self._add_actions([{
            '_index': 'autocomplete',
            '_type': 'term',
            '_source': source
        }])

    def _add_actions(self, actions):
        for action in actions:
            self.actions.append(action)
        if len(self.actions) >= self.bulk_size:
            self._post()

    def _post(self):
        helpers.bulk(self.es, self.actions)
        self.actions = []
        self.logger.info('Posted bulk')
