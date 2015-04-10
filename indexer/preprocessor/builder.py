import argparse
import tarfile
import os
import shelve
import sys
import json

sys.path.append('/Users/benjaminflorin/PycharmProjects/bc-lib-search')

from indexer.preprocessor.oai_reader import OAIReader
from indexer.preprocessor.marc_converter import MARCConverter
from indexer.preprocessor.reporter import Reporter


class Builder(object):
    def __init__(self, oai_reader, marc_reader, reporter):
        """
        :type reporter: indexer.preprocessor.oai_reader.Reporter
        :type oai_reader:  indexer.preprocessor.oai_reader.OAIReader
        :param oai_reader:
        :type marc_reader:  indexer.preprocessor.marc_converter.MARCConverter
        :param marc_reader:
        :return:
        """
        self.records_seen = shelve.open('shelf')

        self.oai_reader = oai_reader
        self.marc_reader = marc_reader
        self.reporter = reporter

        self.current_tarball = ''
        self.current_oai = ''

    def build(self, src_directory, since, until):
        os.chdir(src_directory)
        raw_file_list = os.listdir(src_directory)
        all_files = sorted(raw_file_list, key=lambda x: os.path.getmtime(x), reverse=True)
        tarballs = list(
            filter(lambda x: x.endswith('tar.gz') and until > os.path.getmtime(src_directory + '/' + x) > since,
                   all_files))
        for tarball in tarballs:
            self.reporter.tarball_mtime = os.path.getmtime(src_directory + '/' + tarball)
            self.current_tarball = tarball
            self.read_tarball(src_directory + '/' + tarball)
        self.reporter.report()
        self.reporter.dump_locations()
        self.reporter.dump_collections()

    def read_oai(self, oai_file):
        self.oai_reader.read(oai_file)
        self.reporter.oais_read += 1

        if self.oai_reader.id in self.records_seen:
            self.reporter.skips += 1
        elif self.oai_reader.status == 'deleted':
            self.records_seen[self.oai_reader.id] = True
            self.reporter.deletes += 1
        else:
            try:
                self.read_marc()
            except ValueError as detail:
                self.reporter.report_read_error(self.current_tarball, self.current_tarball)


    def read_marc(self):
        if self.oai_reader.record:
            self.marc_reader.read(self.oai_reader.record)

            if self._only_at_law(self.marc_reader.location):
                self.reporter.law_only += 1
            elif self.marc_reader.restricted:
                self.reporter.restricted += 1
            else:
                self.reporter.creates += 1
                self._write_to_catalog_index()
                self._write_to_autocomplete_index()
            self.records_seen[self.oai_reader.id] = True
        else:
            self.reporter.report_read_error(self.current_tarball, self.current_tarball)

    def read_tarball(self, tarball_file):
        self.reporter.tarballs_read += 1
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
        pull_data = {
            'title': self.marc_reader.title,
            'author': self.marc_reader.author,
            'subjects': self.marc_reader.subjects,
            'location': self.marc_reader.location,
            'issn': self.marc_reader.issn,
            'isbn': self.marc_reader.isbn,
            'collections': self.marc_reader.collections,
            'series': self.marc_reader.series,
            'callnum': self.marc_reader.call_number,
            'notes': self.marc_reader.notes,
            'toc': self.marc_reader.table_of_contents
        }

        data = {}

        for key, value in pull_data.items():
            if value:
                data[key] = value

        self.reporter.add_locations(self.marc_reader.location)
        self.reporter.add_collections(self.marc_reader.collections)

        print(json.dumps(pull_data, ensure_ascii=False))

    def _write_to_autocomplete_index(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MARC records to JSON for export to ElasticSearch')

    parser.add_argument('--src', type=str, help='source directory', required=True)
    parser.add_argument('--dest', type=str, help='destination directory')
    parser.add_argument('--start', type=int, help='timestamp to import from', required=True)
    parser.add_argument('--until', type=int, help='timestamp to import until')

    args = parser.parse_args()

    if args.src and args.start and args.until:
        p = Builder(OAIReader(), MARCConverter(), Reporter())
        p.build(args.src, args.start, args.until)
    else:
        parser.print_help()