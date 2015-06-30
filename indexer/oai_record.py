class OAIRecord(object):
    def __init__(self, oai_string=None, id=None, status=None, index_record=None):
        """

        :param oai_string:
        :param id:
        :param status:
        :type index_record: indexer.index_record.IndexRecord
        :param index_record:
        :return:
        """
        self.oai_string = oai_string
        self.id = id
        self.status = status
        self.index_record = index_record