import json
import bisect

class Categorizer:
	def __init__(self, lccDirectory):
		lccCat = json.load(open(lccDirectory))
		self.lccCat = []
		for e in lccCat:
			self.lccCat.append((e["startNorm"], e["endNorm"], e))
		self.lccCat.sort()
		self.lower_bounds = [lower for lower,_,_ in self.lccCat]
	"""	
	def categorize(self, normalizedLCC):
		index = bisect.bisect(self.lower_bounds, normalizedLCC) - 1
		if index < 0:
			return None
		#print self.lccCat[index], normalizedLCC
		lower, upper, country = self.lccCat[index]
		data = []
		while(normalizedLCC >= lower):
			if normalizedLCC <= upper:
					data.append(self.lccCat[index])
			index += 1
			lower, upper, _ = self.lccCat[index]
		print data, self.categorize2(normalizedLCC)
		return [d[2] for d in data]
	"""			
	def categorize(self, normLCC):   # very slow increases processing time from tens of minutes to hours, possibly sort and do binary search
              	return [d for d in self.lccCat if normLCC <= d[1] and normLCC >= d[0] and d[1] and d[0]]
	
