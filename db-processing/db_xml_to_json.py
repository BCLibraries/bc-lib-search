import xml.etree.ElementTree as ET
import json, sys

class DBXMLToJSON:
	def __init__(self, xml, saveAs):
		self.xml = xml
		self.saveAs = saveAs

	def run(self):
		data = {}
		e = ET.parse(self.xml)

		root = e.getroot()
		for drec in root.iter('DATA_RECORD'): 
			# unique key
			res_num = drec.findtext('RESOURCE_NUMBER')
			meta_id = drec.findtext('METALIB_ID')
			key = res_num + '-' + meta_id

			if key not in data:
				data[key] = {	'resourceNumber': res_num	}	
					
			# add fields
			field_name = self.varConvention(drec.findtext('FIELD_NAME'))
			data[key][field_name] = drec.findtext('FIELD_DATA')

		with open(self.saveAs, 'w+') as f:
			json.dump(data.values(), f) # only objects written, keys ignored
			print 'Processing completed.'

	def varConvention(self, s):
		return (s[:1].lower() + s[1:] if s else '').replace(' ', '')

if __name__=='__main__':
	args = sys.argv
	parser = DBXMLToJSON(xml=args[1], saveAs=args[2])
	parser.run()
