import argparse
import tarfile
import os
import shelve
import sys
import logging
import logging.config
import json

sys.path.append('/Users/benjaminflorin/PycharmProjects/bc-lib-search')

from indexer.oai_reader import OAIReader
from indexer.marc_converter import MARCConverter
from indexer.reporter import Reporter
from indexer.callnumber import normalize
from indexer.categorizer import Categorizer
from indexer.json_writer import JsonWriter
from indexer.elasticsearch_indexer import ElasticSearchIndexer


class Builder(object):
    def __init__(self, oai_reader, marc_reader, categorizer, writers=None):
        """
        :type categorizer: indexer.preprocesor.categorizer.Categorizer
        :type oai_reader:  indexer.oai_reader.OAIReader
        :param oai_reader:
        :type marc_reader:  indexer.marc_converter.MARCConverter
        :param marc_reader:
        :param writers: a list of Writers
        :return:
        """
        self.records_seen = shelve.open('shelf')

        self.oai_reader = oai_reader
        self.marc_reader = marc_reader
        self.categorizer = categorizer
        self.writers = writers

        self.current_tarball = ''
        self.current_oai = ''

        self.logger = logging.getLogger(__name__)


    def build(self, src_directory, since, until):
        os.chdir(src_directory)
        raw_file_list = os.listdir(src_directory)
        all_files = sorted(raw_file_list, key=lambda x: os.path.getmtime(x), reverse=True)
        tarballs = list(
            filter(lambda x: x.endswith('tar.gz') and until > os.path.getmtime(src_directory + '/' + x) > since,
                   all_files))
        for tarball in tarballs:
            self.current_tarball = tarball
            self.read_tarball(src_directory + '/' + tarball)
        for writer in self.writers:
            writer.close()
        self.records_seen.close()

    def read_oai(self, oai_file):
        self.oai_reader.read(oai_file)

        if self.oai_reader.id in self.records_seen:
            pass
        elif self.oai_reader.status == 'deleted':
            for writer in writers:
                writer.delete(self.oai_reader.id)
            self.records_seen[self.oai_reader.id] = True
        else:
            try:
                self.read_marc()
            except ValueError as detail:
                self.logger.error('Error reading {0}'.format(self.current_tarball))


    def read_marc(self):
        if self.oai_reader.record:
            self.marc_reader.read(self.oai_reader.record)

            if self._only_at_law(self.marc_reader.location):
                pass
            elif self.marc_reader.restricted:
                pass
            else:
                self._write_to_catalog_index()
                self._write_to_autocomplete_index()
            self.records_seen[self.oai_reader.id] = True

    def read_tarball(self, tarball_file):
        tar = tarfile.open(tarball_file, 'r', encoding='utf-8')
        for tarinfo in tar:
            self.current_oai = tarinfo.name
            f = tar.extractfile(tarinfo)
            contents = f.read()
            contents = contents.decode('utf-8')
            self.read_oai(contents)


    def _only_at_law(self, locations):
        """
        :type locations: list
        :param locations: a list of locations
        :return:
        """
        if not locations:
            return False
        for location in locations:
            if not location.startswith('LAW'):
                return False
        return True

    def _write_to_catalog_index(self):
        call_nums = self.marc_reader.call_number
        call_nums_norm = [normalize(lcc) for lcc in call_nums]
        locations = self.marc_reader.location
        collections = self.marc_reader.collections
        taxonomies = self.categorizer.categorize(collections=collections, locations=locations, lccs_norm=call_nums_norm)

        pull_data = {
            'title': self.marc_reader.title,
            'author': self.marc_reader.author,
            'subjects': self.marc_reader.subjects,
            'location': locations,
            'issn': self.marc_reader.issn,
            'isbn': self.marc_reader.isbn,
            'collections': collections,
            'series': self.marc_reader.series,
            'callnum': call_nums,
            'notes': self.marc_reader.notes,
            'toc': self.marc_reader.table_of_contents,
            'type': self.marc_reader.type,
            'tax1': set(),
            'tax2': set(),
            'tax3': set(),
            'id': self.oai_reader.id,
            'language': self.marc_reader.lang
        }

        for taxonomy in taxonomies:
            pull_data['tax1'].add(taxonomy[1])
            pull_data['tax2'].add(taxonomy[2])
            try:
                pull_data['tax3'].add(taxonomy[3])
            except KeyError as e:
                pass

        pull_data['tax1'] = list(pull_data['tax1'])
        pull_data['tax2'] = list(pull_data['tax2'])
        pull_data['tax3'] = list(pull_data['tax3'])

        data = {}

        for key, value in pull_data.items():
            if value:
                data[key] = value

        for writer in self.writers:
            writer.add(data)

    def _write_to_autocomplete_index(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MARC records to JSON for export to ElasticSearch')

    parser.add_argument('src', type=str, help='source directory')
    parser.add_argument('--out', type=str, help='destination directory for JSON output', required=False)
    parser.add_argument('--start', type=int, help='timestamp to import from', required=True)
    parser.add_argument('--until', type=int, help='timestamp to import until', required=True)

    args = parser.parse_args()

    path = os.path.join(os.path.dirname(__file__), 'logging.json')

    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)

    if args.src and args.start and args.until:
        this_dir = os.path.dirname(__file__)
        lcc_map = os.path.join(this_dir, 'categories/lcc_flat.json')
        writers = [ElasticSearchIndexer('localhost'), Reporter()]
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            writers.append(JsonWriter.args.out)
        p = Builder(OAIReader(), MARCConverter(), Categorizer(lcc_map), writers)
        p.build(args.src, args.start, args.until)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit('You forgot to enter a parameter')