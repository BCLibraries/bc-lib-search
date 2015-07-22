import sqlite3


class DB(object):
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.cursor = self.connection.cursor()

    def delete_record(self, id):
        self.cursor.execute('DELETE FROM records WHERE id=?', (id,))
        self.connection.commit()

    def scroll_records(self, last_id='0', offset=1000):
        sql = 'SELECT id,fulltext FROM records WHERE id > ? ORDER BY id LIMIT ' + str(offset)
        return self.cursor.execute(sql, (last_id,)).fetchall()

    def insert_record(self, record_buffer, subject_buffer, alttitle_buffer):
        self.cursor.executemany('INSERT OR IGNORE INTO records VALUES (?,?,?,?,1)', record_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO subjects VALUES(?,?,1)', subject_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO alttitles VALUES(?,?,1)', alttitle_buffer)
        self.connection.commit()

    def updated_terms(self):
        sql = """SELECT text, 'subject', count(text)
        FROM subjects
        WHERE dirty=1
        AND text IS NOT NULL
        GROUP BY text
        UNION
        SELECT text, 'alttitle', count(text)
        FROM alttitles
        WHERE dirty=1
        AND text IS NOT NULL
        UNION
        SELECT text, 'alttitle', count(text)
        FROM alttitles
        WHERE dirty=1
        AND text IS NOT NULL
        GROUP BY text
        UNION
        SELECT title, 'title', count(title)
        FROM records
        WHERE dirty=1
        AND title IS NOT NULL
        GROUP BY title
        """
        results = self.cursor.execute(sql)
        #self.reset_dirty_flags()
        return results

    def reset_dirty_flags(self):
        self.cursor.execute('UPDATE subjects SET dirty=0')
        self.cursor.execute('UPDATE alttitles SET dirty=0')
        self.cursor.execute('UPDATE records SET dirty=0')
