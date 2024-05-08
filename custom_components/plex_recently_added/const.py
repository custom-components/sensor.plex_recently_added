from typing import Final

DOMAIN: Final = "plex_recently_added"


DEFAULT_NAME: Final = 'Plex Recently Added'
CONF_TOKEN: Final = 'token'
CONF_MAX: Final = 'max'
CONF_SECTION_TYPES: Final = 'section_types'
ALL_SECTION_TYPES: Final = ["movie", "show", "artist", "photo"]
CONF_SECTION_LIBRARIES: Final = 'section_libraries'
CONF_EXCLUDE_KEYWORDS: Final = 'exclude_keywords'
CONF_ON_DECK: Final = 'on_deck'
CONF_LOCAL: Final = 'is_local'


DEFAULT_PARSE_DICT: Final = {
    'title_default': '$title',
    'line1_default': '$episode',
    'line2_default': '$release',
    'line3_default': '$number - $rating - $runtime',
    'line4_default': '$genres',
    'icon': 'mdi:eye-off'
}