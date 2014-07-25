import json, os
from tokenize import generate_tokens
from acIndex import ACIndex
import re, copy

class ACESFormatter:
	def __init__(self, directory):
		self.directory = directory	

	def run(self):	
		acFiles = [f for f in os.listdir(self.directory) if f.startswith('acComp')]
		count = 0
		for f in acFiles:
			data = json.load(open(self.directory + '/' + f))
			
			esData = []	
			for obj in data:
				esEntry = {}
				esEntry['text'] = obj['text']
				esEntry['name_suggest'] = {}
				
				esEntry['name_suggest']['input'] = [esEntry['text']]
				esEntry['name_suggest']['output'] = esEntry['text']
				esEntry['name_suggest']['weight'] = obj['normalized_rank']*10
				esEntry['name_suggest']['payload'] = { 'type': obj['type'] }
				esData.append(esEntry)

				## ADD NGRAMS
				#if len(esEntry['text'].split()) > 3:
				#	esEntry2 = copy.deepcopy(esEntry)
				#	esEntry2['name_suggest']['input'] = (self.calcNGrams(esEntry['text'].split(), 3))
				#	esEntry2['name_suggest']['weight'] = obj['normalized_rank']/10
				#	esData.append(esEntry2)
			
			with open(self.directory + '/acESData' + str(count) + '.json', 'w+') as acESFile:
				json.dump(esData, acESFile)
				print 'acESData' + str(count) + '.json written.'
				count += 1
	
	def calcNGrams(self, txtList, n):
  		ngramList = zip(*[txtList[i:] for i in range(n)])
		return [" ".join(s) for s in ngramList]

if __name__ == "__main__":
	directory = '../data/es/primoRecs/'
	#indexer = ACIndex(directory)
       	#indexer.run()
	formatter = ACESFormatter('../data/ac/')
	formatter.run()
