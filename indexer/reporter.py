import logging


class Reporter(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.creates = 0
        self.updates = 0
        self.deletes = 0
        self.skips = 0

    def add(self, data):
        self.creates += 1

    def update(self, data):
        self.updates += 1

    def delete(self, data):
        self.deletes += 1

    def skip(self):
        self.skips += 1

    def close(self):
        self.logger.info("Adds: {}".format(self.creates))
        self.logger.info("Skips: {}".format(self.skips))
        self.logger.info("Deletes: {}".format(self.deletes))