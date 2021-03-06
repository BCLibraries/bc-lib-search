import unittest
import pymarc

import io

from indexer.marc_reader import MARCReader


class TestMARCConverter(unittest.TestCase):
    handler = pymarc.XmlHandler()

    with open('marcxml-01.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_basic = handler.records.pop()

    with open('marcxml-02.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_restricted = handler.records.pop()

    with open('marcxml-03.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_ava = handler.records.pop()

    with open('marcxml-04.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_toc = handler.records.pop()

    with open('marcxml-05.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_journal = handler.records.pop()

    with open('marcxml-06.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_music = handler.records.pop()

    with open('marcxml-07.xml', "r") as f:
        xml = f.read().replace('\n', '')
        pymarc.parse_xml(io.StringIO(xml), handler)
        marc_alt_titles = handler.records.pop()

    def setUp(self):
        self.marc_converter = MARCReader()
        self.marc_converter.read(TestMARCConverter.marc_basic)

    def test_title(self):
        self.assertEqual('Capital IQ', self.marc_converter.title)

    def test_author(self):
        self.assertEqual('Chiang, Kai-shek 1887-1975', self.marc_converter.author)

    def test_subjects(self):
        self.maxDiff = None
        expected = ['Business enterprises -- Finance -- Databases',
                    'Industrial statistics -- Databases',
                    'Corporations -- Databases',
                    'Corporations -- Finance -- Databases',
                    'International business enterprises -- Databases',
                    'International business enterprises -- Finance -- Databases',
                    'Consolidation and merger of corporations -- Databases',
                    'Private equity -- Databases',
                    'Marketing research -- Databases',
                    'Electronic reference sources']
        self.assertEqual(expected, self.marc_converter.subjects)

    def test_collection(self):
        self.assertEqual(['RECORD COLLECTION'], self.marc_converter.collections)

    def test_issn(self):
        self.assertEqual(['1234-5678'], self.marc_converter.issn)

    def test_isbn(self):
        self.assertEqual('12345678910', self.marc_converter.isbn)

    def test_restricted(self):
        self.assertFalse(self.marc_converter.restricted)
        self.marc_converter.read(TestMARCConverter.marc_restricted)
        self.assertTrue(self.marc_converter.restricted)

    def test_series(self):
        self.assertEqual(['Series of books'], self.marc_converter.series)

    def test_call_number(self):
        self.marc_converter.read(TestMARCConverter.marc_ava)
        self.assertEqual(['LB1576 .N845 2012', '@350344', 'M019/2006-1 CD045'], self.marc_converter.call_number)

    def test_call_number(self):
        self.marc_converter.read(TestMARCConverter.marc_ava)
        self.assertEqual(['ARCH-IRMA', 'ERC-STACK', 'ONL-KC_STACK'], sorted(self.marc_converter.location))

    def test_toc(self):
        self.marc_converter.read(TestMARCConverter.marc_toc)
        self.assertEqual(['Woefully arrayed / William Cornysh (7:37)'], self.marc_converter.table_of_contents)

    def test_notes(self):
        self.marc_converter.read(TestMARCConverter.marc_ava)
        self.assertEqual(['Found on March 5, 1975, in Richmond, Tex.', 'Generic note field.'],
                         sorted(self.marc_converter.notes))

    def test_publisher(self):
        self.marc_converter.read(TestMARCConverter.marc_ava)
        self.assertEqual('Pearson', self.marc_converter.publisher)

    def test_type(self):
        self.marc_converter.read(TestMARCConverter.marc_ava)
        self.assertEqual('book', self.marc_converter.type)

        self.marc_converter.read(TestMARCConverter.marc_journal)
        self.assertEqual('serial', self.marc_converter.type)

        self.marc_converter.read(TestMARCConverter.marc_basic)
        self.assertEqual('other', self.marc_converter.type)

    def test_uniform_title(self):
        self.marc_converter.read(TestMARCConverter.marc_music)
        self.assertEqual(['Symphonies, no. 3, op. 55, E♭ major'], self.marc_converter.uniform_title)

    def test_var_title(self):
        self.marc_converter.read(TestMARCConverter.marc_alt_titles)
        self.assertEqual(['Pretended simpleton', 'Verstellte Einfalt', 'Fausse naïve'], self.marc_converter.var_title)

    def test_short_title(self):
        self.marc_converter.read(TestMARCConverter.marc_alt_titles)
        self.assertEqual('finta semplice', self.marc_converter.short_title)
