from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging
import hashlib
import time
import math


class ElasticSearchIndexer(object):
    def __init__(self, host, cat_idx='catalog', auto_idx='autocomplete', bulk_size=1000):
        """
        Build the indexer

        :param host: the ElasticSearch host name (e.g. 'localhost')
        :param cat_idx: the name of the catalog index
        :param auto_idx: the name of the autocomplete index
        :param bulk_size: how many actions to post per bulk
        """
        self.es = Elasticsearch([{'host': host}])
        self.actions = []
        self.logger = logging.getLogger(__name__)
        self.bulk_size = bulk_size
        self.cat_idx = cat_idx
        self.auto_idx = auto_idx

    def add_catalog_record(self, oai_record):
        """
        Add a record to the catalog index

        :type oai_record: indexer.oai_record.OAIRecord
        :param oai_record:
        """
        self._add_actions([{
            '_index': self.cat_idx,
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

    def add_autocomplete_term(self, text, subject_cnt, alttitle_cnt, title_cnt, author_cnt):
        """
        Add a term to the autocomplete index

        :param text: the term to add
        :type text: str
        :param subject_cnt: how many times the term appears as a subject
        :type subject_cnt: int
        :param alttitle_cnt: how many times the term appears as an alternate title
        :type alttitle_cnt: int
        :param title_cnt: how many times the term appears as a title
        :type title_cnt: int
        :param author_cnt: how many times the term appears as an author's name
        :type author_cnt: int
        """
        weight = math.ceil(float(subject_cnt) / 10) + author_cnt + 2 * alttitle_cnt + 5 * title_cnt
        self._add_autocomplete_entry(text, [text], weight)

    def _add_autocomplete_entry(self, text, inputs, weight):
        """
        Add an entry to the autocomplete index

        :param text: the entry text
        :type text: str
        :param inputs: a list of inputs to assign the entry
        :type inputs: list
        :param weight: the weight to give the entry
        :type weight: int
        """
        source = {
            'text': text,
            'suggest': {
                'input': self._build_ac_inputs(inputs),
                'output': text,
                'weight': weight
            }
        }
        self._add_actions([{
            '_index': self.auto_idx,
            '_type': 'term',
            '_source': source,
            '_id': self._autocomplete_id(text)
        }])

    @staticmethod
    def _autocomplete_id(text):
        """
        Generate an ID string for an autocomplete index entry

        :param text: the text of the autocomplete term
        :type text: str
        :return: str
        """
        return (hashlib.md5(text.lower().encode('utf-8'))).hexdigest()

    @staticmethod
    def _build_ac_inputs(texts):
        """
        Build a list of inputs for autocomplete

        :param texts: a list of possible input texts
        :type texts: list
        :return: list
        """
        inputs = set()
        for text in texts:
            inputs.add(text)
            lowercase = text.lower()
            if lowercase.startswith('the '):
                inputs.add(text[4:])
            elif lowercase.startswith('an '):
                inputs.add(text[3:])
            elif lowercase.startswith('an '):
                inputs.add(text[3:])
        return list(inputs)

    def _add_actions(self, actions):
        """
        Add actions to the bulk queue

        :param actions: a list of actions
        :type actions: list
        """
        for action in actions:
            self.actions.append(action)
        if len(self.actions) >= self.bulk_size:
            self._post()

    def _post(self):
        """
        Post the queue of bulk actions

        """
        helpers.bulk(self.es, self.actions)
        self.actions = []
        self.logger.info('Posted bulk')
        time.sleep(1)
