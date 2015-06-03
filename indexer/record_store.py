import logging


class RecordStore(object):
    def __init__(self, sqlite3_cursor):
        """

        :type sqlite3_cursor: sqlite3.Cursor
        :return:
        """
        self.logger = logging.getLogger(__name__)
        self.cursor = sqlite3_cursor
        self.connection = sqlite3_cursor.connection

    def add(self, item):
        t = (item['id'], item['title'], item['author'])
        self.cursor.execute('INSERT OR IGNORE INTO records VALUES (?,?,?)', t)
        for subject in item['subjects']:
            t = (item['id'], subject)
            self.cursor.execute('INSERT OR IGNORE INTO subjects VALUES(?,?)', t)
        for alt_title in item['alttitles']:
            t = (item['id'], alt_title)
            self.cursor.execute('INSERT OR IGNORE INTO alttitles VALUES(?,?)', t)
        self.connection.commit()

    def delete(self, item):
        t = (item['id'])
        self.cursor.execute('DELETE FROM subjects WHERE record_id=?', t)
        self.connection.commit()
