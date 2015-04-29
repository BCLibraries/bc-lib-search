from indexer.language_codes import lang_code
import logging


class MARCConverter(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
        return self.marc_record.isbn()

    @property
    def restricted(self):
        return 'CR_RESTRICTED' in self._get_subfields('999', 'a')

    @property
    def series(self):
        return self._get_subfields('490', 'a')

    @property
    def call_number(self):
        callnum = self._get_subfields('AVA', 'd')
        if not any(callnum):
            return []
        else:
            return callnum

    @property
    def location(self):
        return list(set(['-'.join(x.get_subfields('b', 'j')) for x in self.marc_record.get_fields('AVA')]))

    @property
    def table_of_contents(self):
        toc = self._get_subfields('505', 'a')
        if not any(toc):
            return []
        else:
            return toc

    @property
    def notes(self):
        return list(set([x.format_field() for x in self.marc_record.notes()]) - set(self.table_of_contents))

    @property
    def publisher(self):
        return self.marc_record.publisher().rstrip(',.')

    @property
    def type(self):
        if self.marc_record.leader[7] == 'm':
            return 'book'
        elif self.marc_record.leader[7] == 's':
            return 'serial'
        else:
            return 'other'

    @property
    def mms(self):
        return [x.value() for x in self.marc_record.get_fields('001')]

    @property
    def lang(self):
        try:
            code = self.marc_record.get_fields('008')[0].value()[35:38]
        except IndexError as e:
            self.logger.error("no 008 {0}".format(self.mms))
            return None

        try:
            return lang_code[code]
        except KeyError as e:
            self.logger.error("bad lang code '{0}' {1}".format(code, self.mms))
            return None

    def _get_subfields(self, field, subfield):
        return [x[subfield] for x in self.marc_record.get_fields(field)]