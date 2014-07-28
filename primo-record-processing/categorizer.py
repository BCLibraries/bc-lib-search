import json
import sys
import bisect


class Categorizer:
    def __init__(self, lcc_dir):
        self.total_count = 0;
        lcc_cat = json.load(open(lcc_dir))
        self.lcc_cat = []
        for e in lcc_cat:
            self.lcc_cat.append((e["startNorm"], e["endNorm"], e))
        self.lcc_cat.sort()
        self.lower_bounds = [lower for lower, _, _ in self.lcc_cat]

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

    def categorize(self,
                   norm_lcc):  # very slow increases processing time from tens of minutes to hours, possibly sort and do binary search
        self.total_count += 1
        if self.total_count == 1000:
            sys.stdout.write('.')
            self.total_count = 0

        return [d for d in self.lcc_cat if d[1] >= norm_lcc >= d[0] and d[1] and d[0]]
	
