"""
Home Assistant component to feed the Upcoming Media Lovelace card with
recently added media from Plex.

https://github.com/custom-components/sensor.plex_recently_added

https://github.com/custom-cards/upcoming-media-card

"""
import json
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import datetime
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.0.9'

_LOGGER = logging.getLogger(__name__)

CONF_TOKEN = 'token'
CONF_MAX = 'max'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_HOST, default='localhost'): cv.string,
    vol.Optional(CONF_PORT, default=32400): cv.port,
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_MAX, default=5): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([PlexRecentlyAddedSensor(hass, config)], True)


class PlexRecentlyAddedSensor(Entity):

    def __init__(self, hass, conf):
        self.ssl = 's' if conf.get(CONF_SSL) else ''
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.token = conf.get(CONF_TOKEN)
        self.max_items = int(conf.get(CONF_MAX))
        self._state = None
        self.item_count = 0
        self.refresh = False
        self.data = []

    @property
    def name(self):
        return 'Plex_Recently_Added'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        import math
        if self.refresh:
            self.item_count = 0
            attributes = {}
            default = {}
            card_json = []
            default['title_default'] = '$title'
            default['line1_default'] = '$episode'
            default['line2_default'] = '$release'
            default['line3_default'] = '$rating - $runtime'
            default['line4_default'] = '$number - $studio'
            default['icon'] = 'mdi:eye-off'
            card_json.append(default)
            for plex_media in self.data:
                card_item = {}
                directory = '../local/custom-lovelace/upcoming-media-card/images/plex/'
                try:
                    card_item['airdate'] = datetime.utcfromtimestamp(
                        plex_media['addedAt']).isoformat() + 'Z'
                except:
                    continue
                try:
                    if get_days_since(plex_media['addedAt']).days <= 7:
                        card_item['release'] = '$day, $date $time'
                    else:
                        card_item['release'] = '$day, $date $time'
                except:
                    card_item['release'] = '$day, $date $time'
                if 'viewCount' in plex_media:
                    card_item['flag'] = False
                else:
                    card_item['flag'] = True
                if plex_media.get('type') == 'movie':
                    card_item['title'] = plex_media.get('title', '')
                    card_item['episode'] = ''
                elif plex_media.get('type') == 'episode':
                    card_item['title'] = plex_media.get('grandparentTitle', '')
                    card_item['episode'] = plex_media.get('title', '')
                    card_item['number'] = ('S{:02d}E{:02d}').format(
                        plex_media.get('parentIndex', ''),
                        plex_media.get('index', ''))
                else:
                    continue
                if plex_media.get('duration', 0) > 0:
                    card_item['runtime'] = math.floor(
                        plex_media['duration'] / 60000)
                if plex_media.get('rating', 0) > 0:
                    card_item['rating'] = ('\N{BLACK STAR} ' +
                        str(plex_media['rating']))
                else:
                    card_item['rating'] = ''
                try:
                    card_item['poster'] = '{0}p{1}.jpg'.format(
                        directory, plex_media['ratingKey'])
                except:
                    continue
                try:
                    card_item['fanart'] = '{0}f{1}.jpg'.format(
                        directory, plex_media['ratingKey'])
                except:
                    card_item['fanart'] = ''
                self.item_count += 1
                card_json.append(card_item)
            self._state = self.item_count
            self.refresh = False
            attributes['data'] = json.dumps(card_json)
            return attributes

    def update(self):
        import os
        import os.path
        import requests
        from urllib.parse import quote

        api = requests.Session()
        api.verify = False  # Cert is for Plex's domain not our api server
        headers = {"Accept": "application/json", "X-Plex-Token": self.token}
        media_ids = []
        sections = []
        directory = 'www/custom-lovelace/upcoming-media-card/images/plex/'
        recently_added = 'http{0}://{1}:{2}/library/sections/{3}/recentlyAdded?X-Plex-Container-Start=0&X-Plex-Container-Size={4}'
        image_url = 'http{0}://{1}:{2}/photo/:/transcode?width=200&height=200&minSize=1&url={3}%3FX-Plex-Token%3D{4}'
        all_libraries = 'http{0}://{1}:{2}/library/sections/all'

        try:
            libraries = api.get(
                all_libraries.format(self.ssl, self.host, self.port),
                headers=headers, timeout=10)
            for lib_section in libraries.json()['MediaContainer']['Directory']:
                sections.append(lib_section['key'])
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return
        
        if libraries.status_code == 200:
            self.data = []
            for library in sections:
                recent_media = api.get(
                    recently_added.format(
                        self.ssl, self.host, self.port,
                        library, self.max_items * 2),
                    headers=headers, timeout=10)
                self.data += recent_media.json()['MediaContainer']['Metadata']
            self.data = sorted(self.data, key=lambda i: i['addedAt'],
                               reverse=True)[:self.max_items]

            if not os.path.exists(directory):
                os.makedirs(directory)
            for media in self.data:
                media_ids.append(media['ratingKey'])
            if not set(media_ids).issubset(os.listdir(directory)):
                self.refresh = True
                for file in os.listdir(directory):
                    if (file.endswith('jpg') and
                        str(media_ids).find(file) == -1):
                            os.remove(directory + file)
                for media in self.data:
                    if media.get('type') == 'movie':
                        poster = quote(media.get('thumb'))
                        fanart = quote(media.get('art'))
                    elif media.get('type') == 'episode':
                        poster = quote(media.get('grandparentThumb'))
                        fanart = quote(media.get('grandparentArt'))
                    else:
                        continue
                    file_name = media['ratingKey'] + '.jpg'
                    if not os.path.isfile(directory + 'f' + file_name):
                        try:
                            image = api.get(image_url.format(
                                self.ssl, self.host, self.port,
                                fanart, self.token),
                                headers=headers, timeout=10).content
                            open(directory + 'f' + file_name,
                                'wb').write(image)
                        except:
                            pass
                    if not os.path.isfile(directory + 'p' + file_name):
                        try:
                            image = api.get(image_url.format(
                                self.ssl, self.host,self.port,
                                poster, self.token),
                                headers=headers, timeout=10).content
                            open(directory + 'p' + file_name,
                                'wb').write(image)
                        except:
                            continue

def get_days_since(date):
    import dateutil.parser
    import pytz
    now = str(datetime.now().replace(tzinfo=pytz.utc))
    now = dateutil.parser.parse(now)
    date = dateutil.parser.parse(date)
    return (now - date).days
