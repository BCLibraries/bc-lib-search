#!/usr/local/bin/python3

import argparse
import os
import sys
import logging
import logging.config
import json
import time

sys.path.append('/Users/benjaminflorin/PycharmProjects/bc-lib-search')

from indexer.builder import Builder
from indexer.oai_reader import OAIReader
from indexer.marc_converter import MARCConverter
from indexer.reporter import Reporter
from indexer.categorizer import Categorizer
from indexer.json_writer import JsonWriter
from indexer.elasticsearch_indexer import ElasticSearchIndexer
from indexer.db import DB
from indexer.record_store import RecordStore


def main(argv=sys.argv):
    args = get_arguments()
    load_logger(args.log_es)
    lcc_map = os.path.join(os.path.dirname(__file__), 'categories/lcc_flat.json')
    db = DB(args.db)
    records = RecordStore(db)
    writers = get_writers(args)
    with Builder(OAIReader(), MARCConverter(), Categorizer(lcc_map), records, writers,
                 shelve_path=args.shelf) as builder:
        if args.build:
            builder.build(args.src, args.start, args.until)
            os.remove(args.shelf)
        elif args.reindex:
            builder.reindex()

        if args.autoc:
            pass
    db.connection.close()
    sys.exit(0)


def get_arguments():
    parser = argparse.ArgumentParser(description='Convert MARC records to JSON for export to ElasticSearch')
    parser.add_argument('db', type=str, help='SQLite database')
    parser.add_argument('--src', type=str, help='source directory')
    parser.add_argument('--es', type=str, help='ElasticSearch host name')
    parser.add_argument('--out', type=str, help='destination directory for JSON output')
    parser.add_argument('--start', type=int, help='timestamp to import from')
    parser.add_argument('--until', type=int, help='timestamp to import until', default=int(time.time()))
    parser.add_argument('--build', action='store_true', help='rebuild index')
    parser.add_argument('--reindex', action='store_true')
    parser.add_argument('--log_es', action='store_true')
    parser.add_argument('--shelf', help='path to shelf file', default='shelf')
    parser.add_argument('--autoc', action='store_true', help='build autocomplete index')
    return parser.parse_args()


def load_logger(log_elasticsearch=False):
    path = os.path.join(os.path.dirname(__file__), 'logging.json')
    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    if log_elasticsearch:
        logging.getLogger('elasticsearch.trace').propagate = True


def get_writers(args):
    writers = {'reporter': Reporter()}
    if args.es:
        writers['elasticsearch'] = ElasticSearchIndexer(args.es)
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        writers['json'] = JsonWriter(args.out)
    return writers


if __name__ == '__main__':
    sys.exit(main())
