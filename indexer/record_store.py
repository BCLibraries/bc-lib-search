import logging
import zlib


class RecordStore(object):
    MAX_BUFFER = 1000

    def __init__(self, sqlite3_cursor):
        """

        :type sqlite3_cursor: sqlite3.Cursor
        :return:
        """
        self.logger = logging.getLogger(__name__)
        self.cursor = sqlite3_cursor
        self.connection = sqlite3_cursor.connection
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
        t = (item['id'])
        self.cursor.execute('DELETE FROM records WHERE id=?', t)
        self.connection.commit()

    def close(self):
        self._post()

    def _scroll(self, offset=100):
        sql = 'SELECT id,fulltext FROM records WHERE id > ? ORDER BY id LIMIT ' + str(offset)
        self.select_buffer = self.cursor.execute(sql, (self.last_id,)).fetchall()

    def _add_to_buffer(self, buffer, values):
        buffer.append(values)
        if len(buffer) >= RecordStore.MAX_BUFFER:
            self._post()

    def _post(self):
        self.cursor.executemany('INSERT OR IGNORE INTO records VALUES (?,?,?,?,1)', self.record_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO subjects VALUES(?,?,1)', self.subject_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO alttitles VALUES(?,?,1)', self.alttitle_buffer)
        self.connection.commit()
        self.record_buffer = []
        self.subject_buffer = []
        self.alttitle_buffer = []
