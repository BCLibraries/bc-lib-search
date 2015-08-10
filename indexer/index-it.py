#!/usr/local/bin/python3

import argparse
import os
import sys
import logging
import logging.config
import json
import time
import shelve

sys.path.append('/Users/benjaminflorin/PycharmProjects/bc-lib-search')

from indexer.builder import Builder
from indexer.categorizer import Categorizer
from indexer.elasticsearch_indexer import ElasticSearchIndexer
from indexer.db import DB
from indexer.record_store import RecordStore


def main():
    args = get_arguments()
    load_logger()
    args.func(args)
    sys.exit(0)


def index(args):
    builder = get_builder(args)
    builder.index(args.source_dir, args.start, time.time())
    os.remove(args.shelf)


def reindex(args):
    builder = get_builder(args)
    builder.reindex()
    pass


def publish(args):
    records = get_record_store(args)
    shelf = shelve.open(args.shelf)
    es = ElasticSearchIndexer(args.elasticsearch_host, cat_idx=args.cat_idx, auto_idx=args.auto_idx)
    for record in records:
        print(record.subjects)


def autocomplete(args):
    es = ElasticSearchIndexer(args.elasticsearch_host, cat_idx=args.cat_idx, auto_idx=args.auto_idx)
    db = DB(args.sqlite_path)
    for term in db.updated_terms():
        es.add_autocomplete(term[0], term[1], term[2], term[3], term[4])


def get_arguments():
    parser = argparse.ArgumentParser(description='Manage the BC bento search ElasticSearch and SQLite stores')
    subparsers = parser.add_subparsers(help='Subcommands')
    parser.add_argument('--shelf', help='path to shelf file', default='shelf')
    parser.add_argument('--auto_idx', help='ElasticSearch autocomplete index', default='autocomplete')
    parser.add_argument('--cat_idx', help='ElastcSearch catalog index', default='catalog')

    index_parser = subparsers.add_parser('index', help='index new MARC records')
    index_parser.add_argument('source_dir', type=str, help='source directory')
    index_parser.add_argument('sqlite_path', type=str, help='SQLite database')
    index_parser.add_argument('elasticsearch_host', type=str, help='ElasticSearch host name')
    index_parser.add_argument('--start', type=int, help='timestamp to import from', default=1000000)
    index_parser.set_defaults(func=index)

    reindex_parser = subparsers.add_parser('reindex', help='reindex existing MARC records')
    reindex_parser.add_argument('sqlite_path', type=str, help='SQLite database')
    reindex_parser.add_argument('elasticsearch_host', type=str, help='ElasticSearch host name')
    reindex_parser.set_defaults(func=reindex)

    publish_parser = subparsers.add_parser('publish', help='publish from SQLite database to ElasticSearch')
    publish_parser.add_argument('sqlite_path', type=str, help='SQLite database')
    publish_parser.add_argument('elasticsearch_host', type=str, help='ElasticSearch host name')
    publish_parser.set_defaults(func=publish)

    autocmp_parser = subparsers.add_parser('autocomplete', help='build autocomplete index')
    autocmp_parser.add_argument('sqlite_path', type=str, help='SQLite database')
    autocmp_parser.add_argument('elasticsearch_host', type=str, help='ElasticSearch host name')
    autocmp_parser.set_defaults(func=autocomplete)

    return parser.parse_args()


def load_logger():
    path = os.path.join(os.path.dirname(__file__), 'logging.json')
    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)


def get_builder(args):
    lcc_map = os.path.join(os.path.dirname(__file__), 'categories/lcc_flat.json')
    records = get_record_store(args)
    shelf = shelve.open(args.shelf)
    es = ElasticSearchIndexer(args.elasticsearch_host, cat_idx=args.cat_idx, auto_idx=args.auto_idx)
    return Builder(Categorizer(lcc_map), records, es, shelf)


def get_record_store(args):
    db = DB(args.sqlite_path)
    records = RecordStore(db)
    return records


if __name__ == '__main__':
    sys.exit(main())
