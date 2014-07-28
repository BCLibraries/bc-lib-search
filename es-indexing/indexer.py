from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import elasticsearch.helpers
import json, os


class ESIndexer:
    def __init__(self, hosts=None):
        self.es = Elasticsearch(hosts=hosts, sniff_on_connection_fail=True)

    def add_index(self, indexJSON, index, doc_type, alias=None):
        ic = IndicesClient(self.es)
        response = ic.create(index=index, body=json.load(open(indexJSON)))
        if alias: ic.put_alias(index=index, name=alias)
        print indexJSON, response

    def index_data(self, dataJSON, index, doc_type):
        data = json.load(open(dataJSON))
        print dataJSON + '\t' + str(len(data)) + ' records to process.'

        body = [{'_op_type': 'create', '_type': doc_type, '_source': obj} for obj in data if obj]
        response = elasticsearch.helpers.bulk(self.es, index=index, actions=body, stats_only=True)
        print dataJSON, response


if __name__ == "__main__":
    # add command line arg capabilities...eventually

    dataDir = '../../build_indices/data/'
    indexDir = 'indices/'
    es = ESIndexer()

    # add all indices
    es.add_index(indexDir + 'libguides_index.json', 'libguides', 'docs')
    # add other indices . . .

    # index data
    es.index_data('dbClassified.json', 'db', 'metalib')

