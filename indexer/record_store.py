import logging
import zlib
import unicodedata
import sys
from index_record import IndexRecord


class RecordStore(object):
    MAX_BUFFER = 1000

    punctuation_trans_table = dict.fromkeys(
        (i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P')), ' ')

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
        self.term_buffer = {}

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
            oai_record.id, index_record.title, index_record.author,
            zlib.compress(oai_record.oai_string.encode('utf-8')))
        self._add_to_buffer(self.record_buffer, values)
        self.add_term(index_record.title, 'title_cnt')
        self.add_term(index_record.author, 'author_cnt')

        for subject in index_record.subjects:
            values = (oai_record.id, subject)
            self._add_to_buffer(self.subject_buffer, values)
            self.add_term(subject, 'subject_cnt')

        for alt_title in index_record.alttitles:
            values = (oai_record.id, alt_title)
            self._add_to_buffer(self.alttitle_buffer, values)
            self.add_term(alt_title, 'alt_cnt')

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
        self.db.insert_records(self.record_buffer, self.subject_buffer, self.alttitle_buffer)
        self.db.insert_terms(self.term_buffer.values())
        self.record_buffer = []
        self.subject_buffer = []
        self.alttitle_buffer = []
        self.term_buffer = {}

    def add_term(self, term, count_type):
        if term:
            term = self.truncate(term)
            id = self.normalize_term(term)
            try:
                self.term_buffer[id] = {'id': id, 'term': term, 'title_cnt': 0, 'alt_cnt': 0, 'subject_cnt': 0,
                                        'author_cnt': 0}
            except KeyError:
                pass
            self.term_buffer[id][count_type] += 1

    @staticmethod
    def normalize_term(term):
        normalized = term.translate(RecordStore.punctuation_trans_table)
        return ' '.join(normalized.split()).lower()

    @staticmethod
    def truncate(content, length=80, suffix='…'):
        if len(content) <= length:
            return content
        else:
            return content[:length].rsplit(' ', 1)[0] + suffix
