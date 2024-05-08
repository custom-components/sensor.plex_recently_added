from homeassistant.core import HomeAssistant
from .plex_api import PlexApi

def setup_client(
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
    is_local: bool,
    ):
    client = PlexApi(hass, ssl, token, max, on_deck, host, port, section_types, section_libraries, exclude_keywords, is_local)

    client.update()
    return client