import os, json
from pymarc import MARCReader
from pymarc import marcxml
from record import Record
from pnx_to_json import PNXtoJSON
from categorizer import Categorizer
import xml.etree.cElementTree as ET # cElementTree vs. the slower ElementTree (same API)
import gzip

class RecordIterator:	
	def __init__(self, directory, saveDirectory, recordType, matchExp, languageMapperJSON=""):
		"""
			:type directory: basestring
			:param directory: where to load files from

			:type saveDirectory: basestring
			:param saveDirectory: save file location

			:type recordType: basestring
			:param recordType: whether input is Marc binary, MarcXML, or PNX

			:type matchExp: basestring
			:param matchExp: ????? IGNORE

			:type languageMapperJSON: dict
			:param languageMapperJSON: maps Marc language codes in PNX
		"""
		self.saveDirectory = saveDirectory
		self.directory = directory
		self.categorizer = Categorizer('categories/lcc_flat.json') # for class look-up
		self.languageMapper = json.load(open(languageMapperJSON)) if languageMapperJSON else None	
		self.fileNumber = 0
		self.recordType = recordType
		self.matchExp = matchExp

	def run(self):
		count = 0; data = []; saveNIncrements = 1000000
		for mrcFilePath in self.getAllFiles(self.directory, self.matchExp):
			#records = self.records(mrcFilePath)	# record iterator
			#xml = []
			
			# caching parsed xml is much faster
			#for i,record in enumerate(records):	
			#	if i % 10000 == 0: print i
			
			# iterate through cached records	
			print mrcFilePath
			for records in self.chunk(gzip.GzipFile(fileobj=open(mrcFilePath, 'rb')), increments=50000):
				for record in records:
					if "pnx" in self.recordType.lower():
						data.append(PNXtoJSON(record, self.categorizer, self.languageMapper))	

					count += 1
					if count % 10000 == 0:
						print str(count) + " records processed."
				self.save(data)	
				#print "Chunking..."
		self.save(data)	# final write

	def records(self, mrcFilePath):
		if "pnx" in self.recordType.lower():
			return self.xmlSplit(gzip.GzipFile(fileobj=open(mrcFilePath, 'rb'))) # assumes gzipped file

	def xmlSplit(self, handle, separator=lambda x: x.startswith('<?xml')):
		buff = []
		for line in handle:
			if separator(line):
				if buff:
					yield ''.join(buff)
					buff[:] = []
			buff.append(line)
		yield ''.join(buff)

	def chunk(self, handle, increments=50000):
		data = []
		#print "Chunking..."		
		for i in self.xmlSplit(handle):
			try: data.append(ET.fromstring(i))
			except: print "Bad XML"
			if len(data) == increments:
				yield data
				data[:] = []
			if len(data) % 10000 == 0:
				print str(len(data)) + " chunked."
		yield data

	def save(self, data):
		with open(self.saveDirectory + str(self.fileNumber) + '.json', 'w+') as f:
                        json.dump(data, f)
                        print str(len(data)) + " records written.\n" + self.saveDirectory + str(self.fileNumber) + ".json write completed"	
                        del data[:] # delete contents after write
			self.fileNumber += 1

	def getAllFiles(self, directory, file_extension=""):
                """path of all files with given extension
                   in the tree under a given directory
                """
                for root, dirs, files in os.walk(directory):
                        for file in files:
                                if file_extension in file:
                                        yield os.path.join(root, file)

# Run
if __name__=='__main__':
	mrcDirectory = '../../data/split-marc/'
	#r = RecordIterator(mrcDirectory, "./esPrimoRecords", "marc_binary", "mrc")
	#r = RecordIterator('../../data/Marc_Binary/', './esPrimoRecords', 'TMP')
	r = RecordIterator('../../data/Marc_Binary/', '../data/es/esPrimoRecords', recordType='pnx', matchExp='pnx', languageMapperJSON='language_mapping.json')
	r.run()
