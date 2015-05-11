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


def main(argv=sys.argv):
    args = get_arguments()
    load_logger()
    lcc_map = os.path.join(os.path.dirname(__file__), 'categories/lcc_flat.json')
    with Builder(OAIReader(), MARCConverter(), Categorizer(lcc_map), get_writers(args)) as builder:
        builder.build(args.src, args.start, args.until)
    sys.exit(0)


def get_arguments():
    parser = argparse.ArgumentParser(description='Convert MARC records to JSON for export to ElasticSearch')
    parser.add_argument('src', type=str, help='source directory')
    parser.add_argument('--es', type=str, help='ElasticSearch host name')
    parser.add_argument('--out', type=str, help='destination directory for JSON output')
    parser.add_argument('--start', type=int, help='timestamp to import from', required=True)
    parser.add_argument('--until', type=int, help='timestamp to import until', default=int(time.time()))
    parser.add_argument('--build', action='store_true')
    return parser.parse_args()


def load_logger():
    path = os.path.join(os.path.dirname(__file__), 'logging.json')
    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)


def get_writers(args):
    writers = [Reporter()]
    if args.es:
        writers.append(ElasticSearchIndexer(args.es))
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        writers.append(JsonWriter(args.out))
    return writers


if __name__ == '__main__':
    sys.exit(main())