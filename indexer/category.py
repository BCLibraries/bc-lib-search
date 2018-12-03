class Category:
    """
    A taxonomy category node

    A category node is bound by a minimum and maximum LC Call number and contains a dictionary of terms describing the
    category. E.g.

      min_lcc: RC 0581
      max_lcc: RC 0607
      terms: {1: "Science", 2: "Biology", 3: "Microbiology and Immunology"}

    Terms are hierarchical and keyed by rank. Different categories can share the same terms but have different call
    number ranges (e.g. QR 0000 through QR 9999999 is also "Science:::Biology::Microbiology and Immunology").

    Args:
        min_lcc (str): the minimum normalized LC Call number of the node range
        max_lcc (str): the maximum normalized LC Call number of the node range
        terms (list): the hierarchical list of terms (e.g. {1: "Science", 2: "Biology", 3: "Microbiology and Immunology"})

    Attributes:
        min_lcc (str): the minimum normalized LC Call number of the node range
        max_lcc (str): the maximum normalized LC Call number of the node range
        terms (list): the hierarchical list of terms (e.g. {1: "Science", 2: "Biology", 3: "Microbiology and Immunology"})
    """

    def __init__(self, min_lcc, max_lcc, terms):
        """
        :type min_lcc: str
        :type max_lcc: str
        :type terms: list
        """
        self.min_lcc = min_lcc
        self.max_lcc = max_lcc
        self.terms = terms
