from .language_codes import lang_code
import logging

subfields_240 = ['a', 'd', 'f', 'g', 'h', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's']
subfields_246 = ['a', 'b']
subfields_subjects = ['a', 'b', 'c', 'd', 'v', 'x', 'y', 'z']


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
        return [' -- '.join(x.get_subfields(*subfields_subjects)).rstrip('.') for x in self.marc_record.subjects()]

    @property
    def collections(self):
        return self._get_field('940', 'a')

    @property
    def issn(self):
        return self._get_field('022', 'a')

    @property
    def isbn(self):
        return self.marc_record.isbn()

    @property
    def restricted(self):
        return 'CR_RESTRICTED' in self._get_field('999', 'a')

    @property
    def series(self):
        return self._get_field('490', 'a')

    @property
    def call_number(self):
        callnum = self._get_field('AVA', 'd')
        if not any(callnum):
            return []
        else:
            return callnum

    @property
    def location(self):
        return list(set(['-'.join(x.get_subfields('b', 'j')) for x in self.marc_record.get_fields('AVA')]))

    @property
    def table_of_contents(self):
        toc = self._get_field('505', 'a')
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

    @property
    def short_title(self):
        try:
            title_field = self.marc_record.get_fields('245')[0]
        except (TypeError, IndexError):
            self.logger.error("problem in 245 $a: {0}".format(self.mms))
            return None

        try:
            nonfiling = title_field.indicators[1]
            if nonfiling == ' ':
                nonfiling = 0
        except ValueError:
            nonfiling = 0

        try:
            short_title = title_field['a'][int(nonfiling):]
        except TypeError:
            return None

        try:
            short_title += " " + self['245']['b']
        except TypeError:
            pass
        return short_title

    @property
    def uniform_title(self):
        return self._get_field('130', 'a') + self._get_field('240', subfields_240)

    @property
    def var_title(self):
        return [' '.join(field.get_subfields(*subfields_246)) for field in self.marc_record.get_fields('246') if
                field.indicators[0] in ['1', '3']]

    def _get_field(self, code, subfields):
        return [' '.join(field.get_subfields(*subfields)) for field in self.marc_record.get_fields(code)]