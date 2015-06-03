import tarfile
import os
import shelve
import logging
import logging.config
import record_store
from indexer.callnumber import normalize


class Builder(object):
    def __init__(self, oai_reader, marc_reader, categorizer, sqlite3_cursor=None, writers=None, shelve_path='shelf'):
        """
        :type categorizer: indexer.categorizer.Categorizer
        :type oai_reader:  indexer.oai_reader.OAIReader
        :param oai_reader:
        :type marc_reader:  indexer.marc_converter.MARCConverter
        :param marc_reader:
        :type sqlite3_cursor: sqlite3.Cursor
        :param sqlite3_cursor: an sqlite3 cursor for the indexing database
        :param writers: a list of
        :param shelve_path: path to the shelf file
        :return:
        """
        self.records_seen = shelve.open(shelve_path)

        self.oai_reader = oai_reader
        self.marc_reader = marc_reader
        self.categorizer = categorizer
        self.db = sqlite3_cursor
        self.writers = writers
        self.building = False

        if sqlite3_cursor:
            self.records = record_store.RecordStore(sqlite3_cursor)

        self.current_tarball = ''
        self.current_oai = ''

        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for writer in self.writers.values():
            writer.close()
        self.records_seen.close()

    def build(self, src_directory, since, until):
        self.building = True
        os.chdir(src_directory)
        raw_file_list = os.listdir(src_directory)
        all_files = sorted(raw_file_list, key=lambda x: os.path.getmtime(x), reverse=True)
        tarballs = list(
            filter(lambda x: x.endswith('tar.gz') and until > os.path.getmtime(src_directory + '/' + x) > since,
                   all_files))
        for tarball in tarballs:
            self.current_tarball = tarball
            self.read_tarball(src_directory + '/' + tarball)
        self.building = False

    def reindex(self):
        try:
            for oai_string in self.records:
                self.read_oai(oai_string)
        except IndexError:
            pass

    def read_oai(self, oai_string):
        self.oai_reader.read(oai_string)

        if self.building and self.oai_reader.id in self.records_seen:
            self.writers['reporter'].skip()
        elif self.oai_reader.status == 'deleted':
            for writer in self.writers.values():
                writer.delete(self.oai_reader.id)
            self.records_seen[self.oai_reader.id] = True
        else:
            try:
                self.read_marc(oai_string)
            except ValueError as detail:
                self.records_seen[self.oai_reader.id] = True
                self.logger.error('Error reading {0}'.format(self.current_tarball))

    def read_marc(self, oai_string):
        if self.oai_reader.record:
            self.marc_reader.read(self.oai_reader.record)

            if self._only_at_law(self.marc_reader.location):
                pass
            elif self.marc_reader.restricted:
                pass
            else:
                data = self._write_to_catalog_index()
                self.records.add(data, oai_string)
            self.records_seen[self.oai_reader.id] = True

    def read_tarball(self, tarball_file):
        tar = tarfile.open(tarball_file, 'r', encoding='utf-8')
        for tarinfo in tar:
            self.current_oai = tarinfo.name
            try:
                (name, extension) = tarinfo.name.split('.')
            except ValueError:
                name = ''
                self.logger.error('No name or extension: ' + tarinfo.name + " in " + tarball_file)
            record_id = 'urm_publish-' + name
            if not record_id in self.records_seen:
                f = tar.extractfile(tarinfo)
                contents = f.read()
                contents = contents.decode('utf-8')
                self.read_oai(contents)
            else:
                self.writers['reporter'].skip()

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

        data = {
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
            'language': self.marc_reader.lang,
            'alttitles': self.marc_reader.uniform_title + self.marc_reader.var_title
        }

        try:
            data['shorttitle'] = self.marc_reader.short_title
        except ValueError:
            self.logger.error('Short title error in ' + self.oai_reader.id)
            raise

        for taxonomy in taxonomies:
            data['tax1'].add(taxonomy[1])
            data['tax2'].add(taxonomy[2])
            try:
                data['tax3'].add(taxonomy[3])
            except KeyError as e:
                pass

        data['tax1'] = list(data['tax1'])
        data['tax2'] = list(data['tax2'])
        data['tax3'] = list(data['tax3'])

        for writer in self.writers.values():
            writer.add(data)

        return data
