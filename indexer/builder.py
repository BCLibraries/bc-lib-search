import tarfile
import os
import shelve
import logging
import logging.config
import indexer.callnumber as call_number
from indexer import oai_reader


class Builder(object):
    """
    Handles the entire build process



    This is a bit of God object, which is unfortunate.
    """

    def __init__(self, categorizer, records, elasticsearch, records_seen):
        """
        :type categorizer: indexer.categorizer.Categorizer
        :type records: indexer.record_store.RecordStore
        :param records: the record store
        :type elasticsearch: indexer.elasticsearch_indexer.ElasticSearchIndexer
        :param elasticsearch: elasticsearch writer
        :type records_seen: shelve.Shelf
        :param records_seen: a shelf
        :return:
        """
        self.records_seen = records_seen

        self.adds = 0
        self.deletes = 0

        self.categorizer = categorizer
        self.records = records
        self.elasticsearch = elasticsearch
        self.building = False

        self.current_tarball = ''
        self.current_oai = ''

        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Adds: {}".format(self.adds))
        print("Dels: {}".format(self.deletes))
        self.elasticsearch.close()
        self.records_seen.close()
        self.records.close()

    def index(self, src_directory, since, until):
        """

        :param src_directory: the directory containing the source tarballs
        :param since: index only records added after this date
        :param until: index only records added beforet his date
        :return:
        """
        self.building = True
        os.chdir(src_directory)
        raw_file_list = os.listdir(src_directory)
        all_files = sorted(raw_file_list, key=lambda x: os.path.getmtime(x), reverse=True)
        tarballs = list(
            filter(lambda x: x.endswith('tar.gz') and until > os.path.getmtime(src_directory + '/' + x) > since,
                   all_files))
        for tarball in tarballs:
            self.current_tarball = tarball
            full_path = src_directory + '/' + tarball
            if not full_path in self.records_seen:
                self.read_tarball(full_path)
                self.records_seen[full_path] = True
        self.records.close()
        self.building = False

    def reindex(self):
        try:
            for oai_string in self.records:
                self.read_oai(oai_string)
        except IndexError:
            pass

    def read_oai(self, oai_string):
        """
        Reads a single OAI record

        :param oai_string: str
        :return: OAIRecord
        """
        oai_record = oai_reader.read(oai_string)
        return oai_record

    def read_tarball(self, tarball_file):
        """
        Reads a tarball containing multiple OAI records

        :param tarball_file: str
        :return:
        """
        tar = tarfile.open(tarball_file, 'r', encoding='utf-8')
        for tarinfo in tar:
            self.read_tarred_file(tar, tarball_file, tarinfo)

    def read_tarred_file(self, tar, tarball_file, tarinfo):
        """
        Reads a single file from within a tarfile, containing one OAI record

        :param tar:
        :param tarball_file:
        :param tarinfo:
        :return:
        """
        self.current_oai = tarinfo.name
        try:
            (name, extension) = tarinfo.name.split('.')
        except ValueError:
            name = ''
            self.logger.error('No name or extension: ' + tarinfo.name + " in " + tarball_file)
        record_id = 'urm_publish-' + name
        if not record_id in self.records_seen:
            try:
                f = tar.extractfile(tarinfo)
                contents = f.read()
                contents = contents.decode('utf-8')
                oai_record = self.read_oai(contents)

                if oai_record.status == 'deleted':
                    self.delete_record(oai_record.id)
                elif oai_record.status == 'new' or oai_record.status == 'updated':
                    self.add_record(oai_record)
                else:
                    self.logger.error('Generic error - {0}'.format(oai_record.id))

                self.records_seen[oai_record.id] = True

            except ValueError as detail:
                self.logger.exception('Error reading {0}'.format(self.current_tarball))
            except AttributeError as detail:
                self.logger.exception('Error reading {0}'.format(self.current_tarball))

    def delete_record(self, id):
        self.deletes += 1
        self.elasticsearch.delete(id)
        self.records.delete(id)

    def add_record(self, oai_record):
        self.adds += 1
        self._write_to_catalog_index(oai_record)
        self.records.add(oai_record)

    def _only_at_law(self, locations):
        """
        Returns true if a record is Law Library-only

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

    def _write_to_catalog_index(self, oai_record):
        """
        Add a record to the catalog index

        :type oai_record: indexer.oai_record.OAIRecord
        :param oai_record:
        :return:
        """
        index_record = oai_record.index_record
        try:
            call_nums_norm = [call_number.normalize(lcc) for lcc in index_record.callnum]
            taxonomies = self.categorizer.categorize(collections=index_record.collections,
                                                     locations=index_record.location,
                                                     lccs_norm=call_nums_norm)
        except ValueError:
            self.logger.info("Strange callnumber {} for ".format(index_record.callnum, oai_record.id))
            taxonomies = []

        tax1 = set()
        tax2 = set()
        tax3 = set()

        for taxonomy in taxonomies:
            tax1.add(taxonomy[1])
            tax2.add(taxonomy[2])
            try:
                tax3.add(taxonomy[3])
            except KeyError as e:
                pass

        index_record.tax1 = list(tax1)
        index_record.tax2 = list(tax2)
        index_record.tax3 = list(tax3)

        self.elasticsearch.add_catalog_record(oai_record)
