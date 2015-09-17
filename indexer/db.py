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

    def insert_records(self, record_buffer, subject_buffer, alttitle_buffer):
        self.cursor.executemany('INSERT OR IGNORE INTO records VALUES (?,?,?,?,1)', record_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO subjects VALUES(?,?,1)', subject_buffer)
        self.cursor.executemany('INSERT OR IGNORE INTO alttitles VALUES(?,?,1)', alttitle_buffer)
        self.connection.commit()

    def insert_terms(self, term_buffer):
        sql = """
        INSERT OR REPLACE INTO terms (id, term, title_cnt, alt_cnt, subject_cnt, author_cnt, dirty)
        VALUES (
            :id,
            :term,
            COALESCE((SELECT title_cnt + :title_cnt FROM terms WHERE id = :id), :title_cnt),
            COALESCE((SELECT alt_cnt + :alt_cnt FROM terms WHERE id = :id), :alt_cnt),
            COALESCE((SELECT subject_cnt + :subject_cnt FROM terms WHERE id = :id), :subject_cnt),
            COALESCE((SELECT author_cnt + :author_cnt FROM terms WHERE id = :id), :author_cnt),
            1
        );
        """
        self.cursor.executemany(sql, term_buffer)
        self.connection.commit()

    def updated_terms(self):
        sql = """SELECT term, subject_cnt, alt_cnt, title_cnt, author_cnt
        FROM terms
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
