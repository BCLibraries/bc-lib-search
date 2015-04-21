from .category import Category


class IntervalNode:
    def __init__(self, value, left=None, right=None):
        """
        :type value: str
        :param value:

        :type left: IntervalNode
        :param left:

        :type right: IntervalNode
        :param right:

        """
        self.right = right
        self.left = left
        self.value = value
        self.cats_by_start = []
        self.cats_by_end = []

    def add_category(self, category):
        """
        :type category: Category
        """
        self.cats_by_end.append(category)
        self.cats_by_start.append(category)

        self.cats_by_end = sorted(self.cats_by_end, key=lambda category: category.max_lcc, reverse=True)
        self.cats_by_start = sorted(self.cats_by_start, key=lambda category: category.min_lcc)

    def get_matches(self, lcc):
        """
        :type lcc: str
        :return: dict
        """
        results = []

        num_cats = len(self.cats_by_start)

        if self.value <= lcc:

            i = 0
            while i < num_cats and self.cats_by_end[i].max_lcc >= lcc:
                results.append(self.cats_by_end[i].terms)
                i += 1

        else:
            i = 0
            while i < num_cats and self.cats_by_start[i].min_lcc <= lcc:
                results.append(self.cats_by_start[i].terms)
                i += 1

        return results