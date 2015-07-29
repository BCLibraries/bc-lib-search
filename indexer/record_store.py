import logging
import zlib
from index_record import IndexRecord


class RecordStore(object):
    MAX_BUFFER = 1000

    def __init__(self, db):
        """

        :type db: indexer.db.DB
        :return:
        """
        self.logger = logging.getLogger(__name__)
        self.db = db
        self.select_buffer = []
        self.last_id = ''
        self.num_inserts = 0
        self.record_buffer = []
        self.subject_buffer = []
        self.alttitle_buffer = []

    def __iter__(self):
        self.select_buffer = []
        self.last_id = ''
        return self

    def __next__(self):
        if not self.select_buffer:
            self._scroll()
        current = self.select_buffer.pop(0)
        self.last_id = current[0]
        index_record = IndexRecord()
        index_record.id = current[0]
        index_record.subjects = self.db.get_subjects(index_record.id)
        return index_record

    def add(self, oai_record):
        """
        :type oai_record: indexer.oai_record.OAIRecord
        :param oai_record:
        :return:
        """
        index_record = oai_record.index_record
        values = (
        oai_record.id, index_record.title, index_record.author, zlib.compress(oai_record.oai_string.encode('utf-8')))
        self._add_to_buffer(self.record_buffer, values)

        for subject in index_record.subjects:
            values = (oai_record.id, subject)
            self._add_to_buffer(self.subject_buffer, values)

        for alt_title in index_record.alttitles:
            values = (oai_record.id, alt_title)
            self._add_to_buffer(self.alttitle_buffer, values)

    def delete(self, id):
        self.db.delete_record(id)

    def close(self):
        self._post()

    def _scroll(self, offset=100):
        self.select_buffer = self.db.scroll_records(offset=offset, last_id=self.last_id)

    def _add_to_buffer(self, buffer, values):
        buffer.append(values)
        if len(buffer) >= RecordStore.MAX_BUFFER:
            self._post()

    def _post(self):
        self.db.insert_record(self.record_buffer, self.subject_buffer, self.alttitle_buffer)
        self.record_buffer = []
        self.subject_buffer = []
        self.alttitle_buffer = []

    def build_terms(self):
        self.db.build_terms()
