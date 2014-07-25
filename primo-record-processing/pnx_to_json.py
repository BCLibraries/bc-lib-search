import xml.etree.cElementTree as ET
from callnumber import LC
from categorizer import Categorizer
import json, sys, re, string

class PNXtoJSON(dict):
        """PNXtoJSON processes a pnx record from Primo into JSON"""

        def __init__(self, xml, categorizer, languageMapper):
                """
                        :type xml: cElementTree
                        :param xml: XML PNX record
                """
		self.root = xml
		self.categorizer = categorizer
		self.languageMapper = languageMapper
                self.build()

        def build(self):
		# Record ID, some have subfields, most don't
		text = self.getField(xPath="./control/sourcerecordid", forceUnique=True)
		if self.hasSubfields(text):	rID = self.getSubfields(text)["V"]
		else:				rID = text
		self["id"] = rID		

		# Title
		self["title"] = self.getField(xPath="./search/title", forceUnique=True)

		# Other titles
		self["otherTitles"] = self.getField(xPath="./search/alttitle")

		# Subjects
		self["subjects"] = self.getField(xPath="./search/subject")

		# Authors
		self["authors"] = self.getField(xPath="./search/creatorcontrib")

		# Description
		self["description"] = self.getField(xPath="./display/description")

		# Table of Contents
		self["toc"] = self.getField(xPath="./search/toc")

		# ISBN
		self["isbn"] = self.getField(xPath="./search/isbn")

		# ISSN
		self["issn"] = self.getField(xPath="./search/issn")

		# Place of pub.
		self["placeOfPub"] = self.getField(xPath="./search/lsr09")

		# Name of pub.
		self["nameOfPub"] = self.getField(xPath="./search/lsr08")

		# Series
		self["series"] = self.getField(xPath="./search/lsr11")

		# Language
		marcLang = self.getField(xPath="./facets/language")
		self["language"] = [self.languageMapper[lang] for lang in marcLang if lang in self.languageMapper] if marcLang else None

		# Collection
		self["collection"] = self.getField(xPath="./search/lsr30")

		# Resource type
		self["rsrcType"] = self.getField(xPath="./facets/rsrctype")

		# Library
		self["libraryHeld"] = self.getField(xPath="./facets/library")

		# Genre
		self["genre"] = self.getField(xPath="./facets/genre")

		# Metalib ID
		self["metaLibID"] = self.getField(xPath="./search/lsr01")

		# Course #
		self["courseNum"] = self.getField(xPath="./search/lsr02")

		# OCLC #
		self["oclcNum"] = self.getField(xPath="./search/lsr05")

		# Call #
		lcc = self.getField(xPath="./display/availlibrary", forceUnique=True)
		subfields = self.getSubfields(lcc) if lcc else None
		self["LCC"] = re.sub("[\(\)]", "", subfields["2"], 0, 0) if subfields and "2" in subfields else None

		# Normalized call #
		self["LCCNorm"] = None
		if self["LCC"]:
			try:
				normalizer = LC(self["LCC"])
				self["LCCNorm"] = normalizer.normalized
			except: pass

		# LCC Categories
		self["LCCDep1"] = []; self["LCCDep2"] = []; self["LCCDep3"] = []; self["LCCByBranch"] = [];
		if self["LCCNorm"]:
			categories = self.categorizer.categorize(self["LCCNorm"])
			if categories:
				for c in categories:
					c = c[2]
					branch = ""
					for i in range(1,4):
						i = str(i)
						if i in c: 
							if c[i] not in self["LCCDep" + i]:
								self["LCCDep" + i].append(c[i])
							branch += c[i] + "|"
					self["LCCByBranch"].append(branch)
					
	def getField(self, xPath, forceUnique=False):
		data = [e.text for e in self.root.findall(xPath) if e is not None]
		
		if len(data) == 0: 	return None
		elif forceUnique:	return data[0]
		else:			return data
	
	def getSubfields(self, text):
		mapping = {}
		subfields = text.split("$$")
		for subfield in subfields[1:]: 			# first element in split list is just empty string
			mapping[subfield[0]] = subfield[1:]	# map subfield to data, e.g. "D":"infoIsHere"
		return mapping
	
	def hasSubfields(self, text):
		return "$$" in text	
