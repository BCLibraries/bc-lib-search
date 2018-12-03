"""
Dictionaries mapping locations, collection names, languages and  to Taxonomy terms

Sometimes a call number is not the best indicator of what bucket it belongs in. For example, a book about otters in the
main library is the province of the Biology subject specialist, while a book about otters in the Educational Resource
Center belongs to the education subject specialist. These dictionaries handle such special cases.
"""
ARCHIVES = {1: "General Information Sources", 2: "Archives and Manuscripts"}
ERC = {1: "Social Sciences", 2: "Education", 3: "ERC"}
IRISH_MUSIC = {1: "Arts", 2: "Music", 3: "Irish Music"}
IRISH_STUDIES = {1: "International Studies", 2: "British and Irish Studies", 3: "Irish Studies"}
SSW = {1: "Social Sciences", 2: "Social Work"}

COLLECTION_MAP = {
    "BRETHOLZ": [IRISH_MUSIC],
    "CALVER": [IRISH_MUSIC],
    "CANON ROGERS": [IRISH_STUDIES],
    "CONNOLLY, M.J.": [IRISH_MUSIC],
    "CONNOLLY, S.": [IRISH_MUSIC],
    "EGAN": [IRISH_MUSIC],
    "GREEN LINNET": [IRISH_MUSIC],
    "IRISH": [IRISH_STUDIES],
    "IRISH BOUND PAMPHLET COLLECTION": [IRISH_STUDIES],
    "IRISH MUSIC ARCHIVES": [IRISH_MUSIC],
    "IRISH MUSIC ARCHIVES CD": [IRISH_MUSIC],
    "IRISH MUSIC ARCHIVES FOLIOS": [IRISH_MUSIC],
    "IRISH MUSIC ARCHIVES GENERAL": [IRISH_MUSIC],
    "IRISH MUSIC ARCHIVES REF CD": [IRISH_MUSIC],
    "IRISH MUSIC CENTER REFERENCE": [IRISH_MUSIC],
    "IRISH SERIALS": [IRISH_STUDIES],
    "IRISH WOMEN WRITERS, NINETEENTH, EARLY TWENTIETH CENTURY": [IRISH_STUDIES],
    "LANDRETH": [IRISH_STUDIES],
    "LARKIN": [IRISH_STUDIES],
    "O'MALLEY": [IRISH_STUDIES],
    "OCA": [IRISH_STUDIES],
    "OCA IRISH HISTORY": [IRISH_STUDIES],
    "SCHUMAN": [IRISH_MUSIC],
    "SHAFFER": [IRISH_MUSIC],
    "SKY": [IRISH_MUSIC],
    "WOODS": [IRISH_MUSIC],
}

LOCATION_MAP = {
    "ARCH-IMCR": [IRISH_MUSIC],
    "ARCH-IRMA": [IRISH_MUSIC],
    "ARCH-RM115": [IRISH_MUSIC],

    "ARCH-RM305": [ARCHIVES],
    "ARCH-R211A": [ARCHIVES],
    "ARCH-RM211": [ARCHIVES],
    "ARCH-RM404": [ARCHIVES],
    "ARCH-RM306": [ARCHIVES],
    "ARCH-RM206": [ARCHIVES],
    "ARCH-CONG": [ARCHIVES],
    "ARCH-RM210": [ARCHIVES],
    "ARCH-RM303": [ARCHIVES],
    "ARCH-RM300": [ARCHIVES],
    "ARCH-RM304": [ARCHIVES],
    "ARCH-MANU": [ARCHIVES],
    "ARCH-RETRB": [ARCHIVES],
    "ARCH-RM666": [ARCHIVES],
    "ARCH-RM205": [ARCHIVES],
    "ARCH-RM212": [ARCHIVES],
    "ARCH-RM307": [ARCHIVES],
    "ARCH-RM103": [ARCHIVES],
    "ARCH-RM114": [ARCHIVES],
    "ARCH-RM208": [ARCHIVES],
    "ARCH-R111H": [ARCHIVES],
    "ARCH-R111E": [ARCHIVES],
    "ARCH-R111D": [ARCHIVES],
    "ARCH-R111A": [ARCHIVES],
    "ARCH-R111G": [ARCHIVES],
    "ARCH-R111F": [ARCHIVES],
    "ARCH-R111C": [ARCHIVES],
    "ARCH-R111B": [ARCHIVES],
    "ARCH-RM400": [ARCHIVES],
    "ARCH-UNIV": [ARCHIVES],

    "ERC-BBK_14D": [ERC],
    "ERC-CASS_14D": [ERC],
    "ERC-CIRMD_4D": [ERC],
    "ERC-RES_2H": [ERC],
    "ERC-DIE_2H": [ERC],
    "ERC-MAPS_14D": [ERC],
    "ERC-PER_NL": [ERC],
    "ERC-POST_14D": [ERC],
    "ERC-REF_NL": [ERC],
    "ERC-STACK": [ERC],
    "ERC-VIDEO_14D": [ERC],

    "SWC-STACK": [SSW]
}

LANGUAGE_MAP = {
    "Irish": [IRISH_STUDIES]
}
