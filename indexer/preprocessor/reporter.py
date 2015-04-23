import sys
import logging


class Reporter(object):
    def __init__(self):
        self.tarballs_read = 0
        self.tarball_mtime = 0

        self.law_only = 0
        self.restricted = 0
        self.deletes = 0
        self.creates = 0
        self._oais_read = 0
        self.skips = 0

        self.collections = {}
        self.locations = {}

        self.logger = logging.getLogger(__name__)

    def report(self):
        self.logger.info("Tarballs read: {}".format(self.tarballs_read))
        self.logger.info("Tarball mtime: {}".format(self.tarball_mtime))
        self.logger.info("Adds: {}".format(self.creates))
        self.logger.info("Deletes: {}".format(self.deletes))
        self.logger.info("Restricted: {}".format(self.restricted))
        self.logger.info("Law: {}".format(self.law_only))
        self.logger.info("Skipped: {}".format(self.skips))

    def add_locations(self, locations):
        for location in locations:
            if location in self.locations:
                self.locations[location] += 1
            else:
                self.locations[location] = 1

    def add_collections(self, collections):
        for collection in collections:
            if collection in self.collections:
                self.collections[collection] += 1
            else:
                self.collections[collection] = 1

    def dump_collections(self):
        self.logger.info(self.collections)


    def dump_locations(self):
        self.logger.info(self.locations)

    @property
    def oais_read(self):
        return self._oais_read

    @oais_read.setter
    def oais_read(self, value):
        self._oais_read = value

        if self._oais_read % 10000 == 0:
            self.report()
