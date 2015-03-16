from unittest import TestCase
from indexer.preprocessor.pnx_part_reader import PNXPartReader
from indexer.preprocessor.pnx_reader import PNXReader
import xml.etree.cElementTree as ET


class TestPNXReader(TestCase):
    def setUp(self):
        self.pnx_reader = PNXReader()
        self.one_part_pnx = self._load_pnx('pnx-01.xml')
        self.multi_part_pnx = self._load_pnx('pnx-03.xml')

    def test_one_part_record(self):
        self.pnx_reader.read(self.one_part_pnx)
        part_reader = PNXPartReader(self.pnx_reader)
        for part in part_reader.parts():
            expected = {'record_id': ['bc_digitool_mods227088'],
                        'mms': ['99102216760001021'],
                        'source_record_id': ['227088']}
            self.assertEqual(expected, part)

    def _load_pnx(self, filename):
        with open(filename, "r") as myfile:
            data = myfile.read().replace('\n', '')
            return ET.fromstring(data)
        self.re