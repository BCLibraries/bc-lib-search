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

    def scroll_terms(self, last_id='0', offset=1000):
        sql = 'SELECT id,text,type,cnt FROM terms WHERE id > ? ORDER BY id LIMIT ' + str(offset)
        return self.cursor.execute(sql, (last_id,)).fetchall()

    def insert_record(self, record_buffer, subject_buffer, alttitle_buffer):
        self.cursor.executemany('INSERT OR IGNORE INTO records VALUES (?,?,?,?,1)', record_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO subjects VALUES(?,?,1)', subject_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO alttitles VALUES(?,?,1)', alttitle_buffer)
        self.connection.commit()

    def build_terms(self):
        print('building terms...')
        self.cursor.execute(
            """INSERT INTO terms(text,type,cnt,dirty)
            SELECT text, 'subject' AS type, COUNT(text), 1 AS dirty
            FROM subjects
            WHERE dirty=1
            AND text IS NOT NULL
            GROUP BY text"""
        )
        self.cursor.execute(
            """INSERT INTO terms(text,type,cnt,dirty)
            SELECT text, 'alttitle' AS type, COUNT(text), 1 AS dirty
            FROM alttitles
            WHERE dirty=1
            AND text IS NOT NULL
            GROUP BY text"""
        )
        self.cursor.execute(
            """INSERT INTO terms(text,type,cnt,dirty)
            SELECT author, 'author' AS type, COUNT(author), 1 AS dirty
            FROM records
            WHERE dirty=1
            AND author IS NOT NULL
            GROUP BY author"""
        )
        self.cursor.execute(
            """INSERT INTO terms(text,type,cnt,dirty)
            SELECT title, 'title' AS type, COUNT(title), 1 AS dirty
            FROM records
            WHERE dirty=1
            AND title IS NOT NULL
            GROUP BY title"""
        )
        self.cursor.execute('UPDATE subjects SET dirty=0')
        self.cursor.execute('UPDATE alttitles SET dirty=0')
        self.cursor.execute('UPDATE records SET dirty=0')
        self.cursor.connection.commit()
