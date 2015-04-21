from unittest import TestCase
from indexer.preprocessor.categorizer import Categorizer


class TestCallNumberCategorizer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.categorizer = Categorizer('lcc_flat.json')

    def test_categorize_by_callnum(self):
        expected_0 = ['Humanities', 'Germanic Languages and Literatures']

        self.assertEqual(expected_0, self.categorizer.categorize_by_callnum('PT 1937')[0].terms)

        expected_0 = ['Government, Politics and Law', 'Law and Legal Studies']
        expected_1 = ['Humanities', 'Philosophy']
        expected_2 = ['Government, Politics and Law', 'Government Information',
                      'State and Local Government Information']
        cats = self.categorizer.categorize(lcc_norm='K  0341')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[2].terms)
        self.assertEqual(expected_2, cats[1].terms)

        expected_0 = ['Science', 'Biology', 'Zoology']
        expected_1 = ['Science', 'Biology', 'Ecology and Evolutionary Biology']
        cats = self.categorizer.categorize(lcc_norm='QL 073700C250G650 000 2012')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

        expected_0 = ['Social Sciences', 'Sociology']
        expected_1 = ['Social Sciences', 'Social Work']
        cats = self.categorizer.categorize(lcc_norm='HV 088100P725 000 000 2011')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

        expected_0 = ['Humanities', 'American Culture']
        expected_1 = ['Humanities', 'United States History']
        cats = self.categorizer.categorize(lcc_norm='E  017300K870 000 000 2013')
        self.assertEqual(expected_0, cats[0].terms)
        self.assertEqual(expected_1, cats[1].terms)

    def test_categorize_by_location(self):
        IRISH_MUSIC = {1: 'Arts', 2: 'Music', 3: 'Irish Music'}
        ERC = {1: 'Social Sciences', 2: 'Education', 3: 'ERC'}
        ARCHIVES = {1: 'General Information Sources', 2: 'Archives and Manuscripts'}
        self.assertEqual([IRISH_MUSIC], self.categorizer.categorize(location='ARCH-IMCR'))
        self.assertEqual([ARCHIVES], self.categorizer.categorize(location='ARCH-CONG'))
        self.assertEqual([ERC], self.categorizer.categorize(location='ERC-STACK'))

    def test_categorize_by_collection(self):
        IRISH_MUSIC = {1: 'Arts', 2: 'Music', 3: 'Irish Music'}
        IRISH_STUDIES = {1: 'International Studies', 2: 'British and Irish Studies', 3: 'Irish Studies'}
        self.assertEqual([IRISH_MUSIC], self.categorizer.categorize(collection='BRETHOLZ'))
        self.assertEqual([IRISH_STUDIES], self.categorizer.categorize(collection='IRISH SERIALS'))

    def test_combined_categorization(self):
        IRISH_MUSIC = {1: 'Arts', 2: 'Music', 3: 'Irish Music'}
        IRISH_STUDIES = {1: 'International Studies', 2: 'British and Irish Studies', 3: 'Irish Studies'}
        ERC = {1: 'Social Sciences', 2: 'Education', 3: 'ERC'}
        ARCHIVES = {1: 'General Information Sources', 2: 'Archives and Manuscripts'}
        lcc = 'QL 073700C250G650 000 2012'

        # Collection takes precedence over location & call number.
        self.assertEqual([IRISH_MUSIC], self.categorizer.categorize(collection='BRETHOLZ', location='ERC-STACK'))
        self.assertEqual([IRISH_STUDIES], self.categorizer.categorize(collection='IRISH SERIALS', location='ERC-STACK',
                                                                      lcc_norm=lcc))

        # Location takes precedence over call number.
        self.assertEqual([ERC], self.categorizer.categorize(location='ERC-STACK', lcc_norm=lcc))




