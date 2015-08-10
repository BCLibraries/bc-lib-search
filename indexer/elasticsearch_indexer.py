from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging
import hashlib
import time
import math


class ElasticSearchIndexer(object):
    def __init__(self, host, cat_idx='catalog', auto_idx='autocomplete', bulk_size=1000):
        self.es = Elasticsearch([{'host': host}])
        self.actions = []
        self.logger = logging.getLogger(__name__)
        self.bulk_size = bulk_size
        self.cat_indx=cat_idx
        self.auto_indx = auto_idx

    def add(self, oai_record):
        """
        :type oai_record: indexer.oai_record.OAIRecord
        :param oai_record:
        :return:
        """
        self._add_actions([{
            '_index': self.cat_indx,
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

    def add_autocomplete(self, text, subject_cnt, alttitle_cnt, title_cnt, author_cnt):
        term_id = self._autocomplete_id(text)
        weight = 0

        weight = math.ceil(float(subject_cnt) / 10) + author_cnt + 2 * alttitle_cnt + 5 * title_cnt

        source = {
            'text': text,
            'suggest': {
                'input': [text],
                'output': text,
                'weight': weight
            }
        }

        lowercase = text.lower()
        if lowercase.startswith('the '):
            source['suggest']['input'].append(text[4:])
        elif lowercase.startswith('an '):
            source['suggest']['input'].append(text[3:])
        elif lowercase.startswith('an '):
            source['suggest']['input'].append(text[3:])

        self._add_actions([{
            '_index': self.auto_indx,
            '_type': 'term',
            '_source': source,
            '_id': term_id
        }])

    def _autocomplete_id(self, text):
        return (hashlib.md5(text.encode('utf-8'))).hexdigest()

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
