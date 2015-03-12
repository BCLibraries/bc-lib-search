import os, json
from pnx_to_json import PNXtoJSON
from categorizer import Categorizer
import xml.etree.cElementTree as ET  # cElementTree vs. the slower ElementTree (same API)
import gzip
import argparse
from argparse import PARSER


class RecordIterator:
    def __init__(self, src_dir, save_dir, record_type, match_exp, lang_map="", lcc_map=""):
        """
        :type src_dir: str
        :param src_dir: where to load files from

        :type save_dir: str
        :param save_dir: save file location

        :type record_type: str
        :param record_type: whether input is Marc binary, MarcXML, or PNX

        :type match_exp: str
        :param match_exp: ????? IGNORE

        :type lang_map: str
        :param lang_map: maps Marc language codes in PNX

        :type  lcc_map: str
        :param lcc_map: maps lcc range to taxonomy category
        """
        self.lcc_map = lcc_map
        self.save_dir = save_dir
        self.directory = src_dir
        self.categorizer = Categorizer(lcc_map)  # for class look-up
        self.lang_map = json.load(open(lang_map)) if lang_map else None
        self.file_num = 0
        self.rec_type = record_type
        self.match_exp = match_exp

    def run(self):
        data = []
        for marc_file_path in self.get_all_files(self.directory, self.match_exp):
            # iterate through cached records
            print(marc_file_path)
            for records in self.chunk(gzip.GzipFile(fileobj=open(marc_file_path, 'rb')), increments=10000):
                for record in records:
                    data.append(PNXtoJSON(record, self.categorizer, self.lang_map))
                self.save(data)
        self.save(data)  # final write

    def records(self, marc_file_path):
            return self.split_xml(gzip.GzipFile(fileobj=open(marc_file_path, 'rb')))  # assumes gzipped file

    def split_xml(self, handle, separator=lambda x: x.startswith('<?xml')):
        buff = []
        for line in handle:
            if separator(line):
                if buff:
                    yield ''.join(buff)
                    buff[:] = []
            buff.append(line)
        yield ''.join(buff)

    def chunk(self, handle, increments=50000):
        data = []
        for i in self.split_xml(handle):
            try:
                data.append(ET.fromstring(i))
            except:
                print("Bad XML")
            if len(data) == increments:
                yield data
                data[:] = []
        yield data

    def save(self, data):
        with open(self.save_dir + str(self.file_num) + '.json', 'w+') as f:
            json.dump(data, f)
            print((str(len(data)) + " records written.\n" + self.save_dir + str(self.file_num) + ".json write completed"))
            del data[:]  # delete contents after write
            self.file_num += 1

    def get_all_files(self, directory, file_extension=""):
        """
        path of all files with given extension
        in the tree under a given directory
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file_extension in file:
                    yield os.path.join(root, file)

# Run
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MARC records to JSON for export to ElasticSearch')

    parser.add_argument('--src', type=str, help='source directory')
    parser.add_argument('--dest', type=str, help='destination directory')
    parser.add_argument('--type', type=str, choices=['pnx'], help='file type')
    parser.add_argument('--lang', type=str, help='language mapper file (JSON)')
    parser.add_argument('--lcc', type=str, help='lcc mapping file (JSON)')

    args = parser.parse_args()

    if (args.src and args.dest and args.typ and args.lang and args.lcc):
        r = RecordIterator(args.src, args.dest, record_type=args.type, match_exp=args.type, lang_map=args.lang,
                       lcc_map=args.lcc)
        r.run()
    else:
        parser.print_help()