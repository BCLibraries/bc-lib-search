from unittest import TestCase
import indexer.callnumber as CallNumber


class TestCallnumber(TestCase):
    def test_normalization(self):
        self.assertEqual('QL 073700C250G650 000 2012', CallNumber.normalize('QL737.C25 G65 2012'))
        self.assertEqual('HV 088100P725 000 000 2011', CallNumber.normalize('HV881 .P725 2011'))
        self.assertEqual('E  017300K870 000 000 2013', CallNumber.normalize('E173 .K87 2013'))
