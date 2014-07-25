from callnumber import LC
import re

class Record(dict):
	
	def __init__(self, mrc, lccCat):
		"""@parameter mrc: MARCReader class from pymarc
		   @parameter lccCat: lcc category information
		"""
		self.mrc = mrc
		self.lccCat = lccCat
		
		self.extractInfo()

	def extractInfo(self):
		# ID
		if self.mrc['001']:
			self['id'] = self.mrc['001'].format_field()

		# Title
		fields = [('245', 'a', 'b')]
		self['title'] = self.getFields(fields) 

		# Other titles
		fields = [('246', 'a', 'b'),('210', 'a', 'b'),('243', 'a')]
		self['otherTitles'] = self.getFields(fields)

		# Author
		fields= [('100','a'),('110','a','b'),('110','c'),('110','d')]
		self['author'] = self.getFields(fields)

		# Description
		fields = [('520', 'a')]
		self['description'] = self.getFields(fields, filt=lambda s: s.rstrip(':,;/').strip())

		# Subject
		field = '650'
		subfields = ['a', 'v', 'x', 'z']
		self['subject'] = self.getMultiple(field, subfields)

		# ISBN
		field = '020'
		subfields = ['a']
		self['isbn'] = self.getMultiple(field, subfields)

		# ISSN
		fields = [('022', 'a')]
		self['issn'] = self.getFields(fields)

		# Place of publication
		fields = [('260', 'a')]
		self['placeOfPub'] = self.getFields(fields)

		# Name of publication
		fields = [('260', 'b')]
		self['nameOfPub'] = self.getFields(fields)

		# Date of publication
		fields = [('260', 'c')]
		self['dateOfPub'] = self.getFields(fields, filt=lambda s: re.sub("[^0-9]", "", s))

		# Geographic location
		field = '651'
		subfields = ['a']
		self['geoLoc'] = self.getMultiple(field, subfields)

		# Edition
		fields = [('250', 'a', 'b')]
		self['edition'] = self.getFields(fields)

		# Series statement
		fields = [('490', 'a')]
		self['seriesStmt'] = self.getFields(fields)

		# Language
		fields = [('546', 'a')]
		self['language'] = self.getFields(fields)

		# LCC and corresponding categories
		fields = [('050', 'a', 'b')]
		self['LCC'] = self.getFields(fields)
		self['LCCNorm'] = None; self['LCCDep1'] = []; self['LCCDep2'] = []; self['LCCDep3'] = []
		
		if self['LCC'] and self['LCC'].strip():
			try:	# catch and ignore any errors from LC class
				lc = LC(self['LCC'])
				if lc.normalized:
					self['LCCNorm'] = lc.normalized
					lccCats =  self.findRange(self['LCCNorm'])
					for i in range(3, 0, -1): 
						self['LCCDep' + str(i)].extend(list(set([e[str(i)] for e in lccCats if str(i) in e]))) # removes duplicates
			except:
				pass

	def findRange(self, normLCC):	# very slow increases processing time from tens of minutes to hours, possibly sort and do binary search
                return [d for d in self.lccCat if normLCC <= d['endNorm'] and normLCC >= d['startNorm'] and d['startNorm'] and d['endNorm']]

	def getFields(self, fields, filt=lambda s: s.rstrip('?:!.,;/').strip()):
		""" @parameter fields: list of tuples, tuple subfields concatenated, which is then added to a list """
		data = []
		for f in fields:	
                	data.append(filt(' '.join([self.mrc[f[0]][f[i]] for i in range(1, len(f)) if self.subfieldExists(f[0], f[i])])))
		data = filter(None, data)

		if len(data) == 0:	return None
		elif len(data) == 1:	return data[0]
		else:			return data

	def getMultiple(self, field, subfields, filt=lambda s: s.rstrip('?:!.,;/').strip()):
		""" use for multiple instances of a field, e.g. subjects, isbn numbers"""
		data = []
		if self.mrc[field]:
			for subject in self.mrc.get_fields(field):
				for subfield in subject.get_subfields(*subfields):
					data.append(filt(subfield))
			return list(set(data))
	
	def subfieldExists(self, field, subfield):
                if self.mrc[field] and self.mrc[field][subfield] and self.mrc[field][subfield].strip():
                        return True
                else:
                        return False	
