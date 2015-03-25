class MARCConverter(object):
    def read(self, marc_record):
        """
        :type marc_record: pymarc.Record
        :param: marc_record
        :return:
        """
        self.marc_record = marc_record

    @property
    def title(self):
        return self.marc_record.title()

    @property
    def author(self):
        return self.marc_record.author()

    @property
    def subjects(self):
        subject_list = self.marc_record.subjects()
        return [self._format_subjects(x) for x in subject_list]

    def _format_subjects(self, field):
        """
        :type field: pymarc.Field
        :param field:
        :return:
        """
        return ' -- '.join(field.get_subfields('a', 'b', 'c', 'd', 'v', 'x', 'y', 'z')).rstrip('.')

    @property
    def collections(self):
        return self._get_subfields('940', 'a')

    @property
    def issn(self):
        return self._get_subfields('022', 'a')

    @property
    def isbn(self):
        return [self.marc_record.isbn()]

    @property
    def restricted(self):
        return 'CR_RESTRICTED' in self._get_subfields('999', 'a')

    @property
    def series(self):
        return self._get_subfields('490', 'a')

    @property
    def call_number(self):
        return self._get_subfields('AVA', 'd')

    @property
    def location(self):
        return ['-'.join(x.get_subfields('b', 'j')) for x in self.marc_record.get_fields('AVA')]

    @property
    def table_of_contents(self):
        return self._get_subfields('505', 'a')

    @property
    def notes(self):
        return [x.format_field() for x in self.marc_record.notes()]

    @property
    def publisher(self):
        return self.marc_record.publisher().rstrip(',.')

    def _get_subfields(self, field, subfield):
        return [x[subfield] for x in self.marc_record.get_fields(field)]