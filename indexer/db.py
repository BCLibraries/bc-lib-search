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
        sql = """SELECT text, SUM(subject_count), SUM(alt_count), SUM(title_count), SUM(auth_count)
        FROM
        (SELECT text as text, count(text) as subject_count, 0 as alt_count, 0 as title_count, 0 as auth_count
        FROM subjects
        WHERE dirty=1
        AND text IS NOT NULL
        GROUP BY text
        UNION
        SELECT text, 0, count(text), 0, 0
        FROM alttitles
        WHERE dirty=1
        AND text IS NOT NULL
        GROUP BY text
        UNION
        SELECT title, 0, 0, count(title), 0
        FROM records
        WHERE dirty=1
        AND title IS NOT NULL
        GROUP BY title
        UNION
        SELECT author,  0, 0, 0, count(author)
        FROM records
        WHERE dirty=1
        AND author IS NOT NULL
        GROUP BY author)
        GROUP BY text
        """
        results = self.cursor.execute(sql)
        # self.reset_dirty_flags()
        return results

    def reset_dirty_flags(self):
        self.cursor.execute('UPDATE subjects SET dirty=0')
        self.cursor.execute('UPDATE alttitles SET dirty=0')
        self.cursor.execute('UPDATE records SET dirty=0')

    def get_subjects(self, id):
        sql = 'SELECT text FROM subjects WHERE record_id = ?'
        sqlite_response = self.cursor.execute(sql, (id,)).fetchall()
        return DB._extract_row_values(sqlite_response)

    def get_alttitles(self, id):
        sql = 'SELECT text FROM alttitles WHERE record_id = ?'
        return self.cursor.execute(sql, (id,)).fetchall()
        pass

    @staticmethod
    def _extract_row_values(row):
        returnlist = []
        for item in row:
            returnlist.append(item[0])
        return returnlist
