import json, string
import xml.etree.ElementTree as ET
from callnumber import LC


class LCCCatParse:
    def __init__(self, xml):
        self.xml = xml
        self.table = []

    def run(self):
        root = ET.fromstring(open(self.xml).read())
        self.flatten(root, {}, 0)

        with open('lcc_flat.json', 'w+') as f:
            print(str(len(self.table)) + ' call # pairs')
            json.dump(self.table, f)

    def flatten(self, element, ancestors, level):
        level += 1
        for child in element.findall('*'):
            if 'call-numbers' in child.tag:
                a = ancestors.copy()
                a['start'] = child.get('start')
                a['end'] = child.get('end')
                a['startNorm'] = LC(a['start']).normalized
                a['endNorm'] = LC(a['end']).normalized

                # fix bad start-end pairs
                if a['startNorm'] > a['endNorm']:
                    temp = a['startNorm']
                    a['startNorm'] = a['endNorm']
                    a['endNorm'] = temp
                    print("switch")

                self.table.append(a)
            else:
                a = ancestors.copy()
                a[str(level)] = child.get('name')
                self.flatten(child, a, level)


if __name__ == '__main__':
    lcc = LCCCatParse('lcc_categories.xml')
    lcc.run()
