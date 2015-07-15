import xml.etree.cElementTree as ET
from indexer.oai_record import OAIRecord
import marc_reader
import logging
import re
import io
from pymarc import XmlHandler, parse_xml

MARC_XPATH = '{http://www.openarchives.org/OAI/2.0/}ListRecords/{http://www.openarchives.org/OAI/2.0/}record/{http://www.openarchives.org/OAI/2.0/}metadata/{http://www.loc.gov/MARC21/slim}record'

logger = logging.getLogger(__name__)
handler = XmlHandler()


def read(oai):
    """
    Read an OAI file.

    :type oai: str
    :param oai: the OAI record as a string
    """
    doc = ET.fromstring(oai)
    oai_id = _get_id(doc)
    status = _get_status(doc)

    if status == 'deleted':
        return OAIRecord(status='deleted', id=oai_id)

    try:
        oai_string = oai.replace('\n', ' ').replace('\r', '')
        marc_record = _get_marc_record(oai_string)
    except ValueError as detail:
        if str(detail) == 'need more than 0 values to unpack':
            logger.error('Field lacks indicators - {0}'.format(oai_id))
        else:
            logger.exception('Problem reading MARC - {0}'.format(oai_id))
        return OAIRecord(status='error', id=oai_id)
    except AttributeError as detail:
        if str(detail) == "'Field' object has no attribute 'subfields'":
            logger.error('Datafield without subfields - {0}'.format(oai_id))
        else:
            logger.exception('Problem reading MARC - {0}'.format(oai_id))
        return OAIRecord(status='error', id=oai_id)

    return OAIRecord(status=status, id=oai_id, index_record=marc_reader.read(marc_record), oai_string=oai_string)


def _get_id(doc):
    xpath = _format_xpath('{0}ListRecords/{0}record/{0}header/{0}identifier')
    return doc.find(xpath).text.replace(':', '-')


def _get_status(doc):
    xpath = _format_xpath('{0}ListRecords/{0}record/{0}header')
    return doc.find(xpath).attrib['status']


def _get_marc_record(oai_string):
    marc_string = re.search(r'<record .*?/record>', oai_string, re.DOTALL).group()
    parse_xml(io.StringIO(marc_string), handler)
    return handler.records.pop()


def _format_xpath(xpath):
    return xpath.format("{http://www.openarchives.org/OAI/2.0/}", "{http://www.loc.gov/MARC21/slim}")
