import json
from .category import Category
from .interval_node import IntervalNode
from .category_maps import COLLECTION_MAP, LOCATION_MAP, LANGUAGE_MAP


class Categorizer(object):
    """
    Converts normalized LCC call numbers to taxonomy categories

    The categorizer is based on an interval tree (http://en.wikipedia.org/wiki/Interval_tree)
    """

    def __init__(self, lcc_map):
        cat_list = json.load(open(lcc_map))
        categories = self.build_category_list(cat_list)
        self.root = self.add_node(categories)
        self.results = []

    def categorize(self, *, collections=None, locations=None, languages=None, lccs_norm=None):
        result = []

        for collection in collections or []:
            result.extend(COLLECTION_MAP.get(collection, []))
        if result:
            return result

        for location in locations or []:
            result.extend(LOCATION_MAP.get(location, []))
        if result:
            return result

        for language in languages or []:
            result.extend(LANGUAGE_MAP.get(language, []))
        if result:
            return result

        for lcc in lccs_norm or []:
            result.extend(self.categorize_by_callnum(lcc))
        return result

    def build_category_list(self, cat_list):
        """
        :param cat_list: a list of categories pulled from the JSON file
        :type cat_list: list
        :returns a list of categories in lower bound order
        :rtype : list of [Category]
        """
        categories = []
        [categories.append(Categorizer.get_taxonomy_terms(cat)) for cat in cat_list]
        categories = sorted(categories, key=lambda category: category.min_lcc)
        return categories

    @staticmethod
    def get_taxonomy_terms(cat):
        if cat["startNorm"] is not None and cat["endNorm"] is not None:
            terms = {1: cat['1'], 2: cat['2']}
            try:
                terms[3] = cat['3']
            except KeyError:
                pass

            return Category(cat['startNorm'], cat['endNorm'], terms)

    def add_node(self, categories):
        """
        :type categories: list

        :returns an IntervalNode with categories and sub-nodes assigned
        :rtype IntervalNode
        """
        left_cats = []
        spanned_cats = []
        right_cats = []

        center = categories[len(categories) // 2].min_lcc

        node = IntervalNode(center)

        i = 0
        for cat in categories:
            if cat.max_lcc < center:
                left_cats.append(cat)
            elif cat.min_lcc <= center <= cat.max_lcc:
                spanned_cats.append(cat)
            else:
                right_cats = categories[i:]
                break
            i += 1

        [node.add_category(cat) for cat in spanned_cats]

        if left_cats:
            node.left = self.add_node(left_cats)

        if right_cats:
            node.right = self.add_node(right_cats)

        return node

    def categorize_by_callnum(self, lcc_norm):
        """
        Get taxonomy terms for an LC call number

        :type lcc_norm: str
        :param lcc_norm: a normalized LC call number
        :returns a list of relevant categories
        :rtype: Category[]
        """
        if not lcc_norm:
            return []
        self.results = []
        self.find(self.root, lcc_norm)
        return self.results

    def find(self, node, lcc):
        """
        :type node: IntervalNode
        :type lcc: str
        """
        self.results.extend(node.get_matches(lcc))

        if node.value >= lcc and node.left is not None:
            self.find(node.left, lcc)
        elif node.value < lcc and node.right is not None:
            self.find(node.right, lcc)
