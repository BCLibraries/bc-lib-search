from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging
import hashlib
import time
import math


class ElasticSearchIndexer(object):
    def __init__(self, host, bulk_size=1000):
        self.es = Elasticsearch([{'host': host}])
        self.actions = []
        self.logger = logging.getLogger(__name__)
        self.bulk_size = bulk_size

    def add(self, oai_record):
        """
        :type oai_record: indexer.oai_record.OAIRecord
        :param oai_record:
        :return:
        """
        self._add_actions([{
            '_index': 'catalog',
            '_type': 'record',
            '_id': oai_record.id,
            '_source': oai_record.index_record.__dict__
        }])

    def update(self, data):
        pass

    def delete(self, id):
        pass

    def close(self):
        self._post()

    def add_autocomplete(self, text, type=None, weight=None):
        term_id = self._autocomplete_id(text, type)

        if type == 'author':
            weight *= 2
        elif type == 'title':
            weight *= 20
        elif type == 'subject':
            weight = math.ceil(float(weight) / 20)

        source = {
            'text': text,
            'suggest': {
                'input': [text],
                'output': text,
                'payload': {
                    'term': text,
                    'type': type,

                },
                'weight': weight
            }
        }
        self._add_actions([{
            '_index': 'autocomplete',
            '_type': 'term',
            '_source': source,
            '_id': term_id
        }])

    def _autocomplete_id(self, text, type):
        fullstring = text + '-' + type
        return (hashlib.md5(fullstring.encode('utf-8'))).hexdigest()

    def _add_actions(self, actions):
        for action in actions:
            self.actions.append(action)
        if len(self.actions) >= self.bulk_size:
            self._post()

    def _post(self):
        helpers.bulk(self.es, self.actions)
        self.actions = []
        self.logger.info('Posted bulk')
        time.sleep(1)
