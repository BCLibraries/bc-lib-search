from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging


class ElasticSearchIndexer(object):
    def __init__(self, host):
        self.es = Elasticsearch([{'host': host}])
        self.actions = []
        self.logger = logging.getLogger(__name__)
        self.spent_waiting = 0

    def add(self, item):
        self.actions.append({
            "_index": "catalog",
            "_type": "record",
            "_id": item['id'],
            "_source": item
        })
        if len(self.actions) == 1000:
            self.post()

    def post(self):
        helpers.bulk(self.es, self.actions)
        self.actions = []
        self.logger.info('Posted bulk')