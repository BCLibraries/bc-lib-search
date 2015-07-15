from indexer.language_codes import lang_code
import logging
from indexer.index_record import IndexRecord

SUBFIELDS_240 = ['a', 'd', 'f', 'g', 'h', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's']
SUBFIELDS_245 = ['a', 'b', 'f', 'g', 'k', 'n', 'p']
SUBFIELDS_246 = ['a', 'b']
SUBFIELDS_SUBJECTS = ['a', 'b', 'c', 'd', 'v', 'x', 'y', 'z']

logger = logging.getLogger(__name__)


def read(marc_record):
    """
    :type marc_record: pymarc.Record
    :param: marc_record
    :return:
    """
    index_record = IndexRecord()
    index_record.title = title(marc_record)
    index_record.author = author(marc_record)
    index_record.subjects = subjects(marc_record)
    index_record.location = location(marc_record)
    index_record.issn = issn(marc_record)
    index_record.isbn = isbn(marc_record)
    index_record.collections = collections(marc_record)
    index_record.series = series(marc_record)
    index_record.callnum = call_numbers(marc_record)
    index_record.notes = notes(marc_record)
    index_record.toc = table_of_contents(marc_record)
    index_record.type = type(marc_record)
    index_record.id = mms(marc_record)
    index_record.language = lang(marc_record)
    index_record.alttitles = var_title(marc_record) + uniform_title(marc_record)
    index_record.restricted = restricted(marc_record)
    find_errors(marc_record)
    return index_record


def title(marc_record):
    try:
        return _get_field(marc_record, '245', SUBFIELDS_245)[0]
    except (TypeError, IndexError):
        logger.error("problem in 245 $a: {0}".format(mms(marc_record)))
        return None


def author(marc_record):
    return marc_record.author()


def subjects(marc_record):
    return [' -- '.join(x.get_subfields(*SUBFIELDS_SUBJECTS)).rstrip('.') for x in marc_record.subjects()]


def collections(marc_record):
    return _get_field(marc_record, '940', 'a')


def issn(marc_record):
    return _get_field(marc_record, '022', 'a')


def isbn(marc_record):
    return marc_record.isbn()


def restricted(marc_record):
    return 'CR_RESTRICTED' in _get_field(marc_record, '999', 'a')


def series(marc_record):
    return _get_field(marc_record, '490', 'a')


def call_numbers(marc_record):
    callnum = _get_field(marc_record, 'AVA', 'd')
    if not any(callnum):
        return []
    else:
        return callnum


def location(marc_record):
    return list(set(['-'.join(x.get_subfields('b', 'j')) for x in marc_record.get_fields('AVA')]))


def table_of_contents(marc_record):
    toc = _get_field(marc_record, '505', 'a')
    if not any(toc):
        return []
    else:
        return toc


def notes(marc_record):
    return list(set([x.format_field() for x in marc_record.notes()]) - set(table_of_contents(marc_record)))


def publisher(marc_record):
    return marc_record.publisher().rstrip(',.')


def type(marc_record):
    if marc_record.leader[7] == 'm':
        return 'book'
    elif marc_record.leader[7] == 's':
        return 'serial'
    else:
        return 'other'


def mms(marc_record):
    return [x.value() for x in marc_record.get_fields('001')]


def lang(marc_record):
    try:
        code = marc_record.get_fields('008')[0].value()[35:38]
    except IndexError as e:
        logger.error("no 008 - {0}".format(mms(marc_record)))
        return None

    try:
        return lang_code[code]
    except KeyError as e:
        logger.error("bad lang code '{0}' - {1}".format(code, mms(marc_record)))
        return None


def short_title(marc_record):
    try:
        title_field = marc_record.get_fields('245')[0]
    except (TypeError, IndexError):
        logger.error("problem in 245 $a - {0}".format(mms(marc_record)))
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
        short_title += " " + marc_record['245']['b']
    except TypeError:
        pass
    return short_title


def uniform_title(marc_record):
    return _get_field(marc_record, '130', 'a') + _get_field(marc_record, '240', SUBFIELDS_240)


def var_title(marc_record):
    return [' '.join(field.get_subfields(*SUBFIELDS_246)) for field in marc_record.get_fields('246') if
            field.indicators[0] in ['1', '3']]


def _get_field(marc_record, code, subfields):
    return [' '.join(field.get_subfields(*subfields)) for field in marc_record.get_fields(code)]


def find_errors(marc_record):
    try:
        code = marc_record.leader[22]
        if code != '0':
            logger.error('bad character ({0}) in LDR 22 - {1}'.format(code, mms(marc_record)))
    except IndexError as e:
        logger.error('no LDR - {0}'.format(mms(marc_record)))

    try:
        len_008 = len(str(marc_record.get_fields('008')[0].value()))
        if len_008 and len_008 != 40:
            logger.error('bad 008 length {1} - {0}'.format(mms(marc_record),len_008))
    except IndexError:
        pass