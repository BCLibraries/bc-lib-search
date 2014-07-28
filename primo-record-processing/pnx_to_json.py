import xml.etree.cElementTree as ET
from callnumber import LC
from categorizer import Categorizer
import json, sys, re, string


class PNXtoJSON(dict):
    """PNXtoJSON processes a pnx record from Primo into JSON"""

    def __init__(self, xml, categorizer, lang_map):
        """
                :type xml: cElementTree
                :param xml: XML PNX record
        """
        self.root = xml
        self.categorizer = categorizer
        self.lang_map = lang_map
        self.build()

    def build(self):
        # Record ID, some have subfields, most don't
        text = self.get_field(xPath="./control/sourcerecordid", force_unique=True)
        if self.has_subfields(text):
            rID = self.get_subfields(text)["V"]
        else:
            rID = text
        self["id"] = rID

        # Title
        self["title"] = self.get_field(xPath="./search/title", force_unique=True)

        # Other titles
        self["otherTitles"] = self.get_field(xPath="./search/alttitle")

        # Subjects
        self["subjects"] = self.get_field(xPath="./search/subject")

        # Authors
        self["authors"] = self.get_field(xPath="./search/creatorcontrib")

        # Description
        self["description"] = self.get_field(xPath="./display/description")

        # Table of Contents
        self["toc"] = self.get_field(xPath="./search/toc")

        # ISBN
        self["isbn"] = self.get_field(xPath="./search/isbn")

        # ISSN
        self["issn"] = self.get_field(xPath="./search/issn")

        # Place of pub.
        self["placeOfPub"] = self.get_field(xPath="./search/lsr09")

        # Name of pub.
        self["nameOfPub"] = self.get_field(xPath="./search/lsr08")

        # Series
        self["series"] = self.get_field(xPath="./search/lsr11")

        # Language
        marcLang = self.get_field(xPath="./facets/language")
        self["language"] = [self.lang_map[lang] for lang in marcLang if
                            lang in self.lang_map] if marcLang else None

        # Collection
        self["collection"] = self.get_field(xPath="./search/lsr30")

        # Resource type
        self["rsrcType"] = self.get_field(xPath="./facets/rsrctype")

        # Library
        self["libraryHeld"] = self.get_field(xPath="./facets/library")

        # Genre
        self["genre"] = self.get_field(xPath="./facets/genre")

        # Metalib ID
        self["metaLibID"] = self.get_field(xPath="./search/lsr01")

        # Course #
        self["courseNum"] = self.get_field(xPath="./search/lsr02")

        # OCLC #
        self["oclcNum"] = self.get_field(xPath="./search/lsr05")

        # Call #
        lcc = self.get_field(xPath="./display/availlibrary", force_unique=True)
        subfields = self.get_subfields(lcc) if lcc else None
        self["LCC"] = re.sub("[\(\)]", "", subfields["2"], 0, 0) if subfields and "2" in subfields else None

        # Normalized call #
        self["LCCNorm"] = None
        if self["LCC"]:
            try:
                normalizer = LC(self["LCC"])
                self["LCCNorm"] = normalizer.normalized
            except:
                pass

        # LCC Categories
        self["LCCDep1"] = [];
        self["LCCDep2"] = [];
        self["LCCDep3"] = [];
        self["LCCByBranch"] = [];
        if self["LCCNorm"]:
            categories = self.categorizer.categorize(self["LCCNorm"])
            if categories:
                for c in categories:
                    c = c[2]
                    branch = ""
                    for i in range(1, 4):
                        i = str(i)
                        if i in c:
                            if c[i] not in self["LCCDep" + i]:
                                self["LCCDep" + i].append(c[i])
                            branch += c[i] + "|"
                    self["LCCByBranch"].append(branch)

    def get_field(self, xPath, force_unique=False):
        data = [e.text for e in self.root.findall(xPath) if e is not None]

        if len(data) == 0:
            return None
        elif force_unique:
            return data[0]
        else:
            return data

    def get_subfields(self, text):
        mapping = {}
        subfields = text.split("$$")
        for subfield in subfields[1:]:  # first element in split list is just empty string
            mapping[subfield[0]] = subfield[1:]  # map subfield to data, e.g. "D":"infoIsHere"
        return mapping

    def has_subfields(self, text):
        return "$$" in text
