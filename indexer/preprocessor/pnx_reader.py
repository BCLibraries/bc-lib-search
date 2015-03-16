class PNXReader(object):
    def __init__(self):
        pass

    def read(self, pnx):
        """
        :type pnx: str
        :param pnx: XML string containing PNX record
        :return:
        """
        self._pnx = pnx

    def get_field(self, xpath, force_unique=False):
        data = [node.text for node in self._pnx.findall('./' + xpath) if PNXReader.field_has_content(node)]
        if len(data) == 0:
            return []
        elif force_unique:
            return data[0]
        else:
            return data

    def field_has_content(node):
        return node is not None and node.text is not None