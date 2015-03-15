from callnumber import LC
import re


class Record(dict):
    def __init__(self, mrc, lcc_cat):
        """@parameter mrc: MARCReader class from pymarc
           @parameter lcc_cat: lcc category information
        """
        self.mrc = mrc
        self.lcc_cat = lcc_cat

        self.extract()

    def extract(self):
        # ID
        if self.mrc['001']:
            self['id'] = self.mrc['001'].format_field()

        # Title
        fields = [('245', 'a', 'b')]
        self['title'] = self.get_fields(fields)

        # Other titles
        fields = [('246', 'a', 'b'), ('210', 'a', 'b'), ('243', 'a')]
        self['otherTitles'] = self.get_fields(fields)

        # Author
        fields = [('100', 'a'), ('110', 'a', 'b'), ('110', 'c'), ('110', 'd')]
        self['author'] = self.get_fields(fields)

        # Description
        fields = [('520', 'a')]
        self['description'] = self.get_fields(fields, filt=lambda s: s.rstrip(':,;/').strip())

        # Subject
        field = '650'
        subfields = ['a', 'v', 'x', 'z']
        self['subject'] = self.get_multiple(field, subfields)

        # ISBN
        field = '020'
        subfields = ['a']
        self['isbn'] = self.get_multiple(field, subfields)

        # ISSN
        fields = [('022', 'a')]
        self['issn'] = self.get_fields(fields)

        # Place of publication
        fields = [('260', 'a')]
        self['placeOfPub'] = self.get_fields(fields)

        # Name of publication
        fields = [('260', 'b')]
        self['nameOfPub'] = self.get_fields(fields)

        # Date of publication
        fields = [('260', 'c')]
        self['dateOfPub'] = self.get_fields(fields, filt=lambda s: re.sub("[^0-9]", "", s))

        # Geographic location
        field = '651'
        subfields = ['a']
        self['geoLoc'] = self.get_multiple(field, subfields)

        # Edition
        fields = [('250', 'a', 'b')]
        self['edition'] = self.get_fields(fields)

        # Series statement
        fields = [('490', 'a')]
        self['seriesStmt'] = self.get_fields(fields)

        # Language
        fields = [('546', 'a')]
        self['language'] = self.get_fields(fields)

        # LCC and corresponding categories
        fields = [('050', 'a', 'b')]
        self['LCC'] = self.get_fields(fields)
        self['LCCNorm'] = None;
        self['LCCDep1'] = [];
        self['LCCDep2'] = [];
        self['LCCDep3'] = []

        if self['LCC'] and self['LCC'].strip():
            try:  # catch and ignore any errors from LC class
                lc = LC(self['LCC'])
                if lc.normalized:
                    self['LCCNorm'] = lc.normalized
                    lccCats = self.find_range(self['LCCNorm'])
                    for i in range(3, 0, -1):
                        self['LCCDep' + str(i)].extend(
                            list(set([e[str(i)] for e in lccCats if str(i) in e])))  # removes duplicates
            except:
                pass

    def find_range(self,
                  norm_lcc):  # very slow increases processing time from tens of minutes to hours, possibly sort and do binary search
        return [d for d in self.lcc_cat if
                norm_lcc <= d['endNorm'] and norm_lcc >= d['startNorm'] and d['startNorm'] and d['endNorm']]

    def get_fields(self, fields, filt=lambda s: s.rstrip('?:!.,;/').strip()):
        """ @parameter fields: list of tuples, tuple subfields concatenated, which is then added to a list """
        data = []
        for f in fields:
            data.append(
                filt(' '.join([self.mrc[f[0]][f[i]] for i in range(1, len(f)) if self.subfield_exists(f[0], f[i])])))
        data = [_f for _f in data if _f]

        if len(data) == 0:
            return None
        elif len(data) == 1:
            return data[0]
        else:
            return data

    def get_multiple(self, field, subfields, filt=lambda s: s.rstrip('?:!.,;/').strip()):
        """ use for multiple instances of a field, e.g. subjects, isbn numbers"""
        data = []
        if self.mrc[field]:
            for subject in self.mrc.get_fields(field):
                for subfield in subject._get_subfields(*subfields):
                    data.append(filt(subfield))
            return list(set(data))

    def subfield_exists(self, field, subfield):
        if self.mrc[field] and self.mrc[field][subfield] and self.mrc[field][subfield].strip():
            return True
        else:
            return False
