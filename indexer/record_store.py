import logging
import zlib


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
        return zlib.decompress(current[1]).decode('utf-8')

    def add(self, item, oai_string):
        values = (item['id'], item['title'], item['author'], zlib.compress(oai_string.encode('utf-8')))
        self._add_to_buffer(self.record_buffer, values)

        for subject in item['subjects']:
            values = (item['id'], subject)
            self._add_to_buffer(self.subject_buffer, values)

        for alt_title in item['alttitles']:
            values = (item['id'], alt_title)
            self._add_to_buffer(self.alttitle_buffer, values)

    def delete(self, item):
        self.db.delete_record(item['id'])

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
