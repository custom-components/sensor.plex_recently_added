"""
Home Assistant component to feed the Upcoming Media Lovelace card with
recently added media from Plex.

https://github.com/custom-components/sensor.plex_recently_added

https://github.com/custom-cards/upcoming-media-card

"""
import os
import os.path
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
        self._dir = '/custom-lovelace/upcoming-media-card/images/plex/'
        self.img = '{0}{1}{2}{3}.jpg'.format({}, self._dir, {}, {})
        self.ssl = 's' if conf.get(CONF_SSL) else ''
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.token = conf.get(CONF_TOKEN)
        self.max_items = int(conf.get(CONF_MAX))
        self.data = []
        self.api_json = []
        self.card_json = []
        self.media_ids = []
        self.change_detected = False
        self._state = None

    @property
    def name(self):
        return 'Plex_Recently_Added'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        import math
        attributes = {}
        if self.change_detected:
            self.card_json = []
            defaults = {}
            """First item in JSON sets card defaults"""
            defaults['title_default'] = '$title'
            defaults['line1_default'] = '$episode'
            defaults['line2_default'] = '$release'
            defaults['line3_default'] = '$rating - $runtime'
            defaults['line4_default'] = '$number - $studio'
            defaults['icon'] = 'mdi:eye-off'
            self.card_json.append(defaults)
            """Format Plex API values for card's JSON"""
            for media in self.data:
                card_item = {}
                if 'addedAt' not in media:
                    continue
                if 'ratingKey' in media:
                    key = media['ratingKey']
                else:
                    continue
                card_item['airdate'] = datetime.utcfromtimestamp(
                        media['addedAt']).isoformat() + 'Z'
                if get_days_since(card_item['airdate']) <= 7:
                    card_item['release'] = '$day, $date $time'
                else:
                    card_item['release'] = '$day, $date $time'
                if 'viewCount' in media:
                    card_item['flag'] = False
                else:
                    card_item['flag'] = True
                if media['type'] == 'movie':
                    card_item['title'] = media['title']
                    card_item['episode'] = ''
                elif media['type'] == 'episode':
                    card_item['title'] = media['grandparentTitle']
                    card_item['episode'] = media['title']
                    card_item['number'] = ('S{:02d}E{:02d}').format(
                        media['parentIndex'], media['index'])
                else:
                    continue
                if media.get('duration', 0) > 0:
                    card_item['runtime'] = math.floor(
                        media['duration'] / 60000)
                if 'studio' in media:
                    card_item['studio'] = media['studio']
                if 'Genre' in media:
                    card_item['genres'] = ', '.join(
                        [genre['tag'] for genre in media['Genre']][:3])
                if media.get('rating', 0) > 0:
                    card_item['rating'] = ('\N{BLACK STAR} ' +
                                           str(media['rating']))
                else:
                    card_item['rating'] = ''
                if os.path.isfile(self.img.format('www', 'p', key)):
                    card_item['poster'] = self.img.format('../local', 'p', key)
                else:
                    continue
                if os.path.isfile(self.img.format('www', 'f', key)):
                    card_item['fanart'] = self.img.format('../local', 'f', key)
                else:
                    card_item['fanart'] = ''
                self.card_json.append(card_item)
                self.change_detected = False
        attributes['data'] = json.dumps(self.card_json)
        return attributes

    def update(self):
        import requests
        from urllib.parse import quote

        api = requests.Session()
        api.verify = False  # Cert is for Plex's domain not our api server
        headers = {"Accept": "application/json", "X-Plex-Token": self.token}
        all_libraries = 'http{0}://{1}:{2}/library/sections/all'
        image_url = 'http{0}://{1}:{2}/photo/:/transcode?width=200&height=200&minSize=1&url={3}%3FX-Plex-Token%3D{4}'
        recently_added = 'http{0}://{1}:{2}/library/sections/{3}/recentlyAdded?X-Plex-Container-Start=0&X-Plex-Container-Size={4}'

        """Find the ID of all libraries in Plex."""
        sections = []
        try:
            libraries = api.get(
                all_libraries.format(self.ssl, self.host, self.port),
                headers=headers, timeout=10)
            for lib_section in libraries.json()['MediaContainer']['Directory']:
                sections.append(lib_section['key'])
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            return
        if libraries.status_code == 200:
            self.api_json = []
            self._state = 'Online'
            """Get JSON for each library, combine and sort."""
            for library in sections:
                sub_sec = api.get(
                    recently_added.format(
                        self.ssl, self.host, self.port,
                        library, self.max_items * 2),
                    headers=headers, timeout=10)
                self.api_json += sub_sec.json()['MediaContainer']['Metadata']
            self.api_json = sorted(self.api_json, key=lambda i: i['addedAt'],
                                   reverse=True)[:self.max_items]

            directory = 'www' + self._dir
            if not os.path.exists(directory):
                os.makedirs(directory)
            """Make list of images in directory to compare to media IDs."""
            dir_contents = [file[1:-4] for file in os.listdir(directory)]

            """If media ids dont match dir images, update images & sensor."""
            if (not set(self.media_ids).issubset(dir_contents) or
                    not set(dir_contents).issubset(self.media_ids)):
                        self.change_detected = True
                        self.data = self.api_json
                        self.media_ids = []
                        """Create list of new media ID's."""
                        for media in self.data:
                            if 'ratingKey' in media:
                                self.media_ids.append(str(media['ratingKey']))
                            else:
                                continue
                        """Remove images not in media list."""
                        for file in os.listdir(directory):
                            if (file.endswith('jpg') and
                                    str(self.media_ids).find(file) == -1):
                                        os.remove(directory + file)
                        """Retrieve images from Plex if not in dir already."""
                        for media in self.data:
                            if 'type' not in media:
                                continue
                            elif media['type'] == 'movie':
                                poster = quote(media['thumb'])
                                fanart = quote(media['art'])
                            elif media['type'] == 'episode':
                                poster = quote(media['grandparentThumb'])
                                fanart = quote(media['grandparentArt'])
                            poster_jpg = (directory + 'p' +
                                          media['ratingKey'] + '.jpg')
                            fanart_jpg = (directory + 'f' +
                                          media['ratingKey'] + '.jpg')
                            if not os.path.isfile(fanart_jpg):
                                try:
                                    image = api.get(image_url.format(
                                        self.ssl, self.host, self.port,
                                        fanart, self.token),
                                        headers=headers, timeout=10).content
                                    open(fanart_jpg, 'wb').write(image)
                                except:
                                    pass
                            if not os.path.isfile(poster_jpg):
                                try:
                                    image = api.get(image_url.format(
                                        self.ssl, self.host, self.port,
                                        poster, self.token),
                                        headers=headers, timeout=10).content
                                    open(poster_jpg, 'wb').write(image)
                                except:
                                    continue
        else:
            self._state = 'Offline'


def get_days_since(date):
    import dateutil.parser
    import pytz
    now = datetime.now().replace(tzinfo=pytz.utc)
    now = dateutil.parser.parse(str(now))
    date = dateutil.parser.parse(str(date))
    return (now - date).days
