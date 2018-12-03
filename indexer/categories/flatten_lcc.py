import json, string
import xml.etree.ElementTree as ET
from callnumber import LC


class LCCCatParse:
    """
    Flattens the UMich XML Taxonomy into a JSON document

    UMich publishes their taxonomy as hierarchical XML, but it's easier to think in a flat format. This script reads
    their XML document (lcc_categories.xml) and converts it to a JSON document (lcc_flat.json) containing a list of
    objects representing category nodes with the format:

        start:     the starting LC call number of a range
        end:       the ending LC call number of a range
        startNorm: the normalized starting LC call number of a range
        endNorm:   the ending normalized LC call number of a range
        1:         the top-level taxonomy term
        2:         the second-level taxonomy term
        3:         the third-level taxonomy term

    E.g.

        {
            "start": "qk 0",
            "end": "qk 9999.999",
            "startNorm": "QK 0000",
            "endNorm": "QK 9999999",
            "1": "Science",
            "2": "Biology",
            "3": "Botany"
        }

    We only need to run this once, and we can re-use the produced lcc_flat.json.

    Args:
        xml (str): the path to the lcc_categories.xml file
    """
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

                if a['startNorm'] > a['endNorm']:
                    raise Exception('Badly ordered pair: ' + a['start'] + ' %%% ' + a['end'])

                self.table.append(a)
            else:
                a = ancestors.copy()
                a[str(level)] = child.get('name')
                self.flatten(child, a, level)


if __name__ == '__main__':
    lcc = LCCCatParse('lcc_categories.xml')
    lcc.run()
