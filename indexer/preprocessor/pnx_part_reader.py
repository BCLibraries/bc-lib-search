from preprocessor.pnx_reader import PNXReader


class PNXPartReader:
    def __init__(self, pnx_reader):
        """
        :type pnx_reader: PNXReader
        :return:
        """
        self.reader = pnx_reader

    def parts(self):
        data = self.reader.get_field('control/sourcerecordid')
        if len(data) == 0:
            part = {'source_record_id': self._source_record_id(),
                    'record_id': self._record_id(),
                    'mms': self._mms()
                    }
            yield part
        else:
            for source_record_node in data:
                part = {'source_record_id': self._source_record_id(),
                        'record_id': self._record_id(),
                        'mms': self._mms()
                        }
                yield part


    def _source_record_id(self, part_number=None):
        if not part_number:
            return self.reader.get_field('control/sourcerecordid')
        pass

    def _record_id(self, part_number=None):
        if not part_number:
            return self.reader.get_field('control/recordid')
        pass

    def _mms(self, part_order=None):
        if not part_order:
            return self.reader.get_field('display/lds11')
        pass