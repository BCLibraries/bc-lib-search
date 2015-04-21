from unittest import TestCase
from indexer.preprocessor.call_number_categorizer import CallNumberCategorizer


class TestCallNumberCategorizer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.categorizer = CallNumberCategorizer("lcc_flat.json")

    def test_pass(self):
        expected_0 = ['Humanities', 'Germanic Languages and Literatures']

        self.assertEqual(expected_0, self.categorizer.categorize('PT 1937')[0].terms)

        expected_0 = ['Government, Politics and Law', 'Law and Legal Studies']
        expected_1 = ['Humanities', 'Philosophy']
        expected_2 = ['Government, Politics and Law', 'Government Information',
                      'State and Local Government Information']
        cats = self.categorizer.categorize('K  0341')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[2].terms)
        self.assertEqual(expected_2, cats[1].terms)

        expected_0 = ['Science', 'Biology', 'Zoology']
        expected_1 = ['Science', 'Biology', 'Ecology and Evolutionary Biology']
        cats = self.categorizer.categorize('QL 073700C250G650 000 2012')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

        expected_0 = ['Social Sciences', 'Sociology']
        expected_1 = ['Social Sciences', 'Social Work']
        cats = self.categorizer.categorize('HV 088100P725 000 000 2011')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

        expected_0 = ['Humanities', 'American Culture']
        expected_1 = ['Humanities', 'United States History']
        cats = self.categorizer.categorize('E  017300K870 000 000 2013')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

