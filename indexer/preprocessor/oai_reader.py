import xml.etree.cElementTree as ET
from io import StringIO
from pymarc import XmlHandler, parse_xml


class OAIReader(object):
    """
    Reads an Alma-generated OAI-PMH file

    Usage:
        reader = OAIReader()
        reader.read(oai_string)
        if reader.status == 'new':
            marc_record = reader.record

    Attributes:
        id              The OAI-PMH identifier
        record          The MARC record inside the OAI-PMH record
        restricted      Is the record restricted for publication?
        status          The OAI-PMH record status ("new" or "delete")

    """
    _marc_xpath = '{http://www.openarchives.org/OAI/2.0/}ListRecords/{http://www.openarchives.org/OAI/2.0/}record/{http://www.openarchives.org/OAI/2.0/}metadata/{http://www.loc.gov/MARC21/slim}record'

    _valid_statuses = ['new', 'deleted', 'updated']

    def __init__(self):
        self.handler = XmlHandler()

    def read(self, oai):
        """
        Read an OAI file.

        :type oai: str
        :param oai: the OAI record as a string
        """
        self.doc = ET.fromstring(oai)

    @property
    def id(self):
        """
        The OAI-PMH record id

        :rtype: str
        :return: the OAI-PMH record id
        """
        xpath = self._format_xpath('{0}ListRecords/{0}record/{0}header/{0}identifier')
        return self.doc.find(xpath).text.replace(':', '-')

    @property
    def status(self):
        """
        The OAI-PMH command

        :rtype: str
        :return: one of "new", "deleted", or "updated"
        """
        xpath = self._format_xpath('{0}ListRecords/{0}record/{0}header')
        status = self.doc.find(xpath).attrib['status']
        if status not in OAIReader._valid_statuses:
            raise OAIError(status + ' is not a valid OAI record status')
        return self.doc.find(xpath).attrib['status']

    @property
    def record(self):
        """
        The MARC record attached to the OAI record

        :rtype: pymarc.Record
        :return: The MARC record
        """
        results = self.doc.find(self._marc_xpath)
        if results:
            xml = ET.tostring(results,encoding='utf-8').decode()
            parse_xml(StringIO(xml), self.handler)
            return self.handler.records.pop()
        else:
            return None

    @staticmethod
    def _format_xpath(xpath):
        return xpath.format("{http://www.openarchives.org/OAI/2.0/}", "{http://www.loc.gov/MARC21/slim}")


class OAIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
