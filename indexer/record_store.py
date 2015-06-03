import logging
import zlib


class RecordStore(object):
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
        t = (item['id'], item['title'], item['author'], zlib.compress(oai_string.encode('utf-8')))
        self.cursor.execute('INSERT OR IGNORE INTO records VALUES (?,?,?,?)', t)
        for subject in item['subjects']:
            t = (item['id'], subject)
            self.cursor.execute('INSERT OR IGNORE INTO subjects VALUES(?,?)', t)
        for alt_title in item['alttitles']:
            t = (item['id'], alt_title)
            self.cursor.execute('INSERT OR IGNORE INTO alttitles VALUES(?,?)', t)
        self.connection.commit()

    def delete(self, item):
        t = (item['id'])
        self.cursor.execute('DELETE FROM records WHERE id=?', t)
        self.connection.commit()

    def _scroll(self, offset=100):
        sql = 'SELECT id,fulltext FROM records WHERE id > ? ORDER BY id LIMIT ' + str(offset)
        self.select_buffer = self.cursor.execute(sql, (self.last_id,)).fetchall()
