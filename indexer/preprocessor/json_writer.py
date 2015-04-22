import os
import json


class JsonWriter(object):
    def __init__(self, output_dir, recs_per_file=1000):
        """
        :type output_dir: str
        :param output_dir: Full path to output directory
        :type recs_per_file: int
        :param recs_per_file: number of records per file
        :return:
        """
        self.recs_per_file = recs_per_file
        self.file_counter = 0
        self.records_in_file = self.recs_per_file + 1
        self.write_fh = None
        """:type : io.TextIOWrapper"""
        self.output_dir = output_dir

    def __del__(self):
        if self.write_fh:
            self.write_fh.close()

    def write(self, data):
        """
        Write a record to permanent storage
        :param data: the data to write, in some format that can be converted to JSON
        :return:
        """
        if self.records_in_file > self.recs_per_file:
            self.open_file()

        self.write_fh.write(json.dumps(data,sort_keys=True) + "\n")
        self.records_in_file += 1

    def open_file(self):
        if self.write_fh:
            self.write_fh.close()

        while os.path.exists(self.output_dir + "/%s.xml" % self.file_counter):
            self.file_counter += 1

        self.write_fh = open(self.output_dir + "/%s.xml" % self.file_counter, "w")
        self.records_in_file = 0

    def write_to_file(self, data):
        pass