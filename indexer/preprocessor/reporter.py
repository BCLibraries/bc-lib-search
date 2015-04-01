import sys
import json


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

    def report(self):
        print("Tarballs read: {}".format(self.tarballs_read))
        print("Tarball mtime: {}".format(self.tarball_mtime))
        print("Adds: {}".format(self.creates))
        print("Deletes: {}".format(self.deletes))
        print("Restricted: {}".format(self.restricted))
        print("Law: {}".format(self.law_only))
        print("Skipped: {}".format(self.skips))
        sys.stdout.flush()

    def report_read_error(self, tarball, oai):
        print('Error reading ' + tarball + ':' + oai, file=sys.stderr)

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
        print(json.dumps(self.collections, indent=4))
        sys.stdout.flush()


    def dump_locations(self):
        print(json.dumps(self.locations, indent=4))
        sys.stdout.flush()

    @property
    def oais_read(self):
        return self._oais_read

    @oais_read.setter
    def oais_read(self, value):
        self._oais_read = value

        if self._oais_read % 10000 == 0:
            self.report()
