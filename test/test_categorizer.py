from unittest import TestCase
from indexer.preprocessor.categorizer import Categorizer


class TestCallNumberCategorizer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.categorizer = Categorizer('lcc_flat.json')

    def test_categorize_by_callnum(self):
        AMER_CULT = {1: 'Humanities', 2: 'American Culture'}
        ECOLOGY = {1: 'Science', 2: 'Biology', 3: 'Ecology and Evolutionary Biology'}
        GERMANIC_LANG = {1: 'Humanities', 2: 'Germanic Languages and Literatures'}
        LEGAL_STUDIES = {1: 'Government, Politics and Law', 2: 'Law and Legal Studies'}
        PHILOSOPHY = {1: 'Humanities', 2: 'Philosophy'}
        SOCIAL_WORK = {1: 'Social Sciences', 2: 'Social Work'}
        SOCIOLOGY = {1: 'Social Sciences', 2: 'Sociology'}
        STATE_GOV = {1: 'Government, Politics and Law', 2: 'Government Information',
                     3: 'State and Local Government Information'}
        US_HIST = {1: 'Humanities', 2: 'United States History'}
        ZOOLOGY = {1: 'Science', 2: 'Biology', 3: 'Zoology'}

        self.assertEqual([GERMANIC_LANG], self.categorizer.categorize(lcc_norm='PT 1937'))
        self.assertEqual([LEGAL_STUDIES, STATE_GOV, PHILOSOPHY], self.categorizer.categorize(lcc_norm='K  0341'))
        self.assertEqual([ZOOLOGY, ECOLOGY], self.categorizer.categorize(lcc_norm='QL 073700C250G650 000 2012'))
        self.assertEqual([SOCIOLOGY, SOCIAL_WORK], self.categorizer.categorize(lcc_norm='HV 088100P725 000 000 2011'))
        self.assertEqual([AMER_CULT, US_HIST], self.categorizer.categorize(lcc_norm='E  017300K870 000 000 2013'))

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




