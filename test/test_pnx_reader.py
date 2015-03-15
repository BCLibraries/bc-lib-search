from unittest import TestCase
from indexer.preprocessor.pnx_reader import PNXReader
import xml.etree.cElementTree as ET


class TestPNXReader(TestCase):
    def setUp(self):
        self.reader = PNXReader()
        self.pnx = self._load_pnx('pnx-01.xml')
        self.reader.read(self.pnx)

    def test_title(self):
        expected = '[Members of the Boston College Class of 1956 studying, possibly at Bapst].'
        self.assertEqual(expected, self.reader.title)

    def test_authors(self):
        expected = ['Boston College. University Archives',
                    'Boston College',
                    'University Archives']
        self.assertEqual(expected, self.reader.authors)

    def test_description(self):
        expected = ['Source of title: Supplied by cataloger.',
                    'Number on item: 401-34643 BC.',
                    'BC99-171']
        self.assertEqual(expected, self.reader.descriptions)

    def test_isbn(self):
        expected = ['123456789']
        self.assertEqual(expected, self.reader.isbn)

    def test_isbn(self):
        expected = ['1234-5678']
        self.assertEqual(expected, self.reader.issn)

    def test_rtype(self):
        expected = ['images']
        self.assertEqual(expected, self.reader.rtype)

    def test_genre(self):
        expected = ['black-and-white prints (photographs)']
        self.assertEqual(expected, self.reader.genre)

    def test_library(self):
        expected = ['Burns', 'Bapst']
        self.assertEqual(expected, self.reader.library)

    def test_toc(self):
        expected = ['1. The first picture; 2. The second picture']
        self.assertEqual(expected, self.reader.toc)

    def test_course(self):
        expected = ['ART1030', 'ART1541']
        self.assertEqual(expected, self.reader.course)

    def test_collection(self):
        expected = ['Boston College Digital Collections']
        self.assertEqual(expected, self.reader.collection)

    def test_series(self):
        expected = ['Pictures of life at Boston College']
        self.assertEqual(expected, self.reader.series)

    def test_languages(self):
        expected = ['English', 'Old Norse']
        self.assertEqual(expected, self.reader.languages)

    def test_missing_field_yields_empty_list(self):
        pnx = self._load_pnx('pnx-02.xml')
        self.reader.read(pnx)
        self.assertEqual([], self.reader.languages)

    def test_empty_field_yields_no_value(self):
        expected = ['Source of title: Supplied by cataloger.',
                    'BC99-171']
        pnx = self._load_pnx('pnx-02.xml')
        self.reader.read(pnx)
        self.assertEqual(expected, self.reader.descriptions)

    def _load_pnx(self, filename):
        with open(filename, "r") as myfile:
            data = myfile.read().replace('\n', '')
            return ET.fromstring(data)