from unittest import TestCase
from preprocessor.oai_reader import OAIReader, OAIError


class TestPNXReader(TestCase):
    def setUp(self):
        self.oai_reader = OAIReader()
        self.create_oai = self._load_oai('oai-01.xml')
        self.delete_oai = self._load_oai('oai-02.xml')

    def test_create_status(self):
        self.oai_reader.read(self.create_oai)
        self.assertEqual('new', self.oai_reader.status)

    def test_delete_status(self):
        self.oai_reader.read(self.delete_oai)
        self.assertEqual('deleted', self.oai_reader.status)

    def test_bad_status(self):
        self.oai_reader.read(self._load_oai('oai-03.xml'))
        with self.assertRaises(OAIError):
             self.oai_reader.status

    def test_id(self):
        self.oai_reader.read(self.create_oai)
        self.assertEqual('urm_publish-61441201100001021', self.oai_reader.id)

    def test_record(self):
        self.oai_reader.read(self.create_oai)
        self.assertEqual(self.oai_reader.record.title(), 'Capital IQ')

    def _load_oai(self, filename):
        with open(filename, "r") as myfile:
            return myfile.read().replace('\n', '')
