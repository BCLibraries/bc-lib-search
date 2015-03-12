import unittest
from indexer.preprocessor.pnx_dump_reader import PNXDumpReader


class TestPNXDumpReader(unittest.TestCase):
    def test_read_produces_correct_results(self):
        expected = ['<?xml version="1.0"?>\n<body>\n    <line>1</line>\n</body>\n', '<body>\n    <line>2\n</body>\n',
                    '<body>\n    <line>3</line>\n</body>']
        dump = PNXDumpReader('pnxdump-01.xml.gz')
        results = list(x for x in dump.read())
        self.assertEqual(expected, results)


if __name__ == '__main__':
    unittest.main()