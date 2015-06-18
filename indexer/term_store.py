class TermStore(object):
    def __init__(self, db, last_term_id):
        """

        :type db: indexer.db.DB
        :return:
        """
        self.db = db
        self.last_id = last_term_id
        self.buffer = []

    def __iter__(self):
        self.buffer = []
        return self

    def __next__(self):
        if not self.buffer:
            self.buffer = self.db.scroll_terms(self.last_id)
        if not self.buffer:
            self.last_id = 0
            raise StopIteration
        current = self.buffer.pop(0)
        self.last_id = current[0]
        return current
