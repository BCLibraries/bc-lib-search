from __future__ import division
import json, timeit
from collections import Counter
import string, math, json, os, sys
import regex, re


class ACIndex:
    """
        JSON autocomplete structure for ES:
                {
                        "text":"",
                        "type":"",
                        "type_count":""
                        "normalized_rank":""
                }

                type can be (currently) "title", "subject", "author", "service", "database", "libguides"
    """

    def __init__(self, jsonDirectory):
        self.jsonDirectory = jsonDirectory
        self.acData = []
        self.titles = Counter()
        self.subjects = Counter()
        self.authors = Counter()

    def run(self):
        start = timeit.default_timer();
        count = 0;
        print 'Iterating through JSON...'

        # Iterate through records and extract desired fields (See self.processJSON)
        for files in os.listdir(self.jsonDirectory):
            count += 1
            print files + " processed. File #" + str(count)
            if files.endswith('.json'):
                with open(self.jsonDirectory + '/' + files) as f:
                    self.processJSON(json.load(f))
        print 'Input JSON processed. All counters have been generated.'

        print 'Counts:\tTitles: ' + str(len(self.titles)) + '\tSubjects: ' + str(
            len(self.subjects)) + '\tAuthors: ' + str(len(self.authors))

        # Buid JSON
        self.processCounter(self.titles, 'title')
        # self.processCounter(self.subjects, 'subject')
        #self.processCounter(self.authors, 'author')

        # Write JSON
        print 'Write complete.\nAutocomplete JSON constructed'
        stop = timeit.default_timer()
        print str(round(stop - start)) + ' seconds for completion'

    def processCounter(self, counter, typeOf):
        total = sum(counter.values())

        count = 0
        fileNumber = 0
        print 'Writing data...'
        for k, v in counter.iteritems():
            temp = {
            'text': k.encode('utf8'),  # 'original': self.original[k],
            'type': typeOf,
            'type_count': v,
            'normalized_rank': int(round((1 / -math.log(v / total)) * 1000000))
            }
            self.acData.append(temp)
            count += 1
            if count % 50000 == 0:
                with open('../data/ac/acComplete' + str(fileNumber) + '.json', 'w+') as f:
                    fileNumber += 1
                    json.dump(self.acData, f)
                    del self.acData[:]
                    print str(count) + " processed."


    def processJSON(self, json):
        for record in json:

            # Titles
            if record['title']: self.titles[self.textProcess(record['title'])] += 1
            if isinstance(record['otherTitles'], list):
                for e in record['otherTitles']:
                    self.titles[self.textProcess(e)] += 1
            """
            # Subjects
            if isinstance(record['subjects'], list):
                                for e in record['subjects']:
                                        self.subjects[self.textProcess(e)] += 1

            # Authors
            if isinstance(record['authors'], list):
                                for e in record['authors']:
                                        self.authors[self.textProcess(e)] += 1
            """

    def textProcess(self, string):
        return ' '.join(self.remove_punctuation(string.lower()).split())

    def remove_punctuation(self, txt):
        return regex.sub(ur"[^\P{P}-]+", "", txt)

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]


if __name__ == '__main__':
    indexer = ACIndex('../data/es/primoRecs/')
    indexer.run()
