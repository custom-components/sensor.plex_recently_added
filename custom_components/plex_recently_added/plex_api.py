from pytz import timezone
from xml.etree import ElementTree
import requests

from homeassistant.core import HomeAssistant
from .const import DEFAULT_PARSE_DICT
from .parser import parse_data, parse_library


import logging
_LOGGER = logging.getLogger(__name__)

class PlexApi():
    def __init__(
        self,
        hass: HomeAssistant,
        ssl: bool,
        token: str,
        max: int,
        on_deck: bool,
        host: str,
        port: int,
        section_types: list,
        section_libraries: list,
        exclude_keywords: list,
        is_local: bool
    ):
        self._hass = hass
        self._ssl = 's' if ssl else ''
        self._token = token
        self._max = max
        self._on_deck = on_deck
        self._host = host
        self._port = port
        self._section_types = section_types
        self._section_libraries = section_libraries
        self._exclude_keywords = exclude_keywords
        self._is_local = is_local

    def update(self):
        if self._is_local:
            info_url = 'http{0}://{1}:{2}'.format(
                self._ssl,
                self._host,
                self._port
            )
        else: 
            info_url = 'http{0}://{1}'.format(
                self._ssl,
                self._host,
            )

        """ Getting the server identifier """
        try:
            info_res = requests.get(info_url + "/", headers={
                "X-Plex-Token": self._token
            }, timeout=10)
            try:
                root = ElementTree.fromstring(info_res.text)
            except:
                _LOGGER.error(info_res.text)
                raise ElementTree.ParseError
            identifier = root.get("machineIdentifier")
        except OSError as e:
            raise FailedToLogin

        url_base = f'{info_url}/library/sections'
        all_libraries = f'{url_base}/all'
        recently_added = (url_base + '/{0}/recentlyAdded?X-Plex-Container-Start=0&X-Plex-Container-Size={1}')
        on_deck = (url_base + '/{0}/onDeck?X-Plex-Container-Start=0&X-Plex-Container-Size={1}')

        """Find the ID of all libraries in Plex."""
        sections = []
        libs = []
        try:
            libraries = requests.get(all_libraries, headers={
                "X-Plex-Token": self._token
            }, timeout=10)
            try:
                root = ElementTree.fromstring(libraries.text)
            except:
                _LOGGER.error(libraries.text)
                raise ElementTree.ParseError
            for lib in root.findall("Directory"):
                libs.append(lib.get("title"))
                if lib.get("type") in self._section_types and (len(self._section_libraries) == 0 or lib.get("title") in self._section_libraries):
                    sections.append(lib.get("key"))
        except OSError as e:
            raise FailedToLogin

        """ Looping through all libraries (sections) """
        data = []
        for library in sections:
            recent_or_deck = on_deck if self._on_deck else recently_added
            sub_sec = requests.get(recent_or_deck.format(library, self._max * 2), headers={
                "X-Plex-Token": self._token
            }, timeout=10)
            try:
                root = ElementTree.fromstring(sub_sec.text)
            except:
                _LOGGER.error(sub_sec.text)
                raise ElementTree.ParseError
            data += parse_library(root)

        return {
            "data": {"data": [DEFAULT_PARSE_DICT] + parse_data(data, self._max, info_url, self._token, identifier)}, 
            "online": True,
            "libraries": libs
        }
    

class FailedToLogin(Exception):
    "Raised when the Plex user fail to Log-in"
    pass