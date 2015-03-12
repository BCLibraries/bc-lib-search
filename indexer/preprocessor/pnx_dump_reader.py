import gzip

class PNXDumpReader:
    def __init__(self, gzip_file):
        """
        :type gzip_file: str
        :param gzip_file: the path to a gzipped PNX dump
        :return:
        """
        self.file = gzip.open(gzip_file,"rt")
        self.buffer = []

    def read(self):
        """
        :rtype: str
        :return str
        """
        for line in self.file:
            xml = self._readline(line)
            if (xml):
                yield xml
        yield self._build_xml()

    def _readline(self, line):
        if line.startswith('<?xml'):
            xml = self._build_xml()
            if xml:
                return xml
        self.buffer.append(line)

    def _build_xml(self):
        xml = ''.join(self.buffer)
        self.buffer[:] = []
        return xml