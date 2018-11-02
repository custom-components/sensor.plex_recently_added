"""
Plex component to feed the Upcoming Media Lovelace card for Home Assistant.

"""
import logging, time, re, os, os.path, json, math, requests, urllib.parse
from datetime import date, datetime
import voluptuous as vol, homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.0.6'

_LOGGER = logging.getLogger(__name__)

CONF_TOKEN = 'token'
CONF_ITEMS = 'item_count'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_HOST, default='localhost'): cv.string,
    vol.Optional(CONF_PORT, default=32400): cv.port,
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_ITEMS, default=5): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([PlexRecentlyAddedSensor(hass, config)],True)

class PlexRecentlyAddedSensor(Entity):

    def __init__(self, hass, conf):
        from pytz import timezone
        self._tz = timezone(str(hass.config.time_zone))
        self.now = str(get_date(self._tz))
        self.ssl = 's' if conf.get(CONF_SSL) else ''
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.token = conf.get(CONF_TOKEN)
        self.items = int(conf.get(CONF_ITEMS))
        self._state = None
        self.attribNum = 0
        self.data = []

    @property
    def name(self):
        return 'Plex_Recently_Added'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        """Return JSON for the sensor."""
        self.attribNum = 0
        attributes = {}
        default = {}
        data = []
        default['title_default'] = '$title'
        default['line1_default'] = '$episode'
        default['line2_default'] = '$release'
        default['line3_default'] = '$rating - $runtime'
        default['line4_default'] = '$number - $studio'
        default['icon'] = 'mdi:eye-off'
        data.append(default)
        for show in self.data[:self.items]:
            pre = {}
            directory = '../local/custom-lovelace/upcoming-media-card/images/plex/'
            if show.get('type') == 'movie':
                self.attribNum += 1
                pre['title'] = show.get('title', '')
                pre['episode'] = ''
            elif show.get('type') == 'episode':
                self.attribNum += 1
                pre['title'] = show.get('grandparentTitle', '')
                pre['episode'] = show.get('title', '')
                pre['number'] = ('S{:02d}E{:02d}').format(
                    show.get('parentIndex', ''), show.get('index', ''))
            else: continue
            if 'viewCount' in show: pre['flag'] = False
            else: pre['flag'] = True
            if show.get('rating', 0) > 0:
                pre['rating'] = '\N{BLACK STAR}' + str(show['rating'])
            else: pre['rating'] = ''
            pre['airdate'] = datetime.utcfromtimestamp(
                show.get('addedAt')).isoformat() + 'Z'
            if show.get('duration', 0) > 0:
                pre['runtime'] = math.floor(show['duration'] / 60000)
            try: pre['poster'] = '{0}p{1}.jpg'.format(directory,show['ratingKey'])
            except: pre['poster'] = ''
            try: pre['fanart'] = '{0}f{1}.jpg'.format(directory,show['ratingKey'])
            except: pre['fanart'] = ''
            pre['release'] = '$day, $date $time'
            data.append(pre)
        self._state = self.attribNum
        attributes['data'] = json.dumps(data)
        return attributes

    def update(self):
        session = requests.Session()
        session.verify = False # Cert is for Plex's domain not our api server
        media_ids = []
        sections = []
        directory = 'www/custom-lovelace/upcoming-media-card/images/plex/'
        recently_added = ('http{0}://{1}:{2}/library/sections/{3}/recentlyAdded?'
            'X-Plex-Token={4}&X-Plex-Container-Start=0&X-Plex-Container-Size={5}')
        image_url = ('http{0}://{1}:{2}/photo/:/transcode?width=200&height=200&'
            'minSize=1&url={3}%3FX-Plex-Token%3D{4}&X-Plex-Token={4}')
        libraries = 'http{0}://{1}:{2}/library/sections/all/?X-Plex-Token={3}'

        """Get all library section keys"""
        try:lib = session.get(libraries.format(
                self.ssl, self.host, self.port, self.token),
                headers={ 'Accept': 'application/json' }, timeout=10)
            for lib_sec in lib.json()['MediaContainer']['Directory']:
                sections.append(lib_sec['key'])
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return

        """Get JSON from each library section, combine, and sort"""
        if lib.status_code == 200:
            self.data = []
            for key in sections:
                recent = session.get(recently_added.format(
                    self.ssl, self.host, self.port, key, self.token, self.items),
                    headers={ 'Accept': 'application/json' }, timeout=10)
                self.data += recent.json()['MediaContainer']['Metadata']
            self.data = sorted(self.data, key = lambda i: i['addedAt'], reverse=True)
    
            if not os.path.exists(directory): os.makedirs(directory)
            for show in self.data[:self.items]: media_ids.append(show['ratingKey'])
    
            """Compare directory contents to media list for missing images"""
            if not set(media_ids).issubset(os.listdir(directory)):
                """Delete image if item is no longer in list"""
                for file in os.listdir(directory):
                    if file.endswith('jpg') and str(media_ids).find(file[1:-4]) == -1: 
                        os.remove(directory + file)
                """Get resized images from Plex photo/:/transcode"""
                for show in self.data[:self.items]:
                    if show.get('type') == 'movie':
                        poster = urllib.parse.quote_plus(show.get('thumb'))
                        fanart = urllib.parse.quote_plus(show.get('art'))
                    elif show.get('type') == 'episode': 
                        poster = urllib.parse.quote_plus(show.get('grandparentThumb'))
                        fanart = urllib.parse.quote_plus(show.get('grandparentArt'))
                    else: continue
                    if not os.path.isfile(directory + 'f' + show['ratingKey'] + '.jpg'):
                        try:r = session.get(image_url.format(
                            self.ssl, self.host, self.port, fanart, self.token)).content
                            open(directory + 'f' + show['ratingKey'] + '.jpg', 'wb').write(r)
                        except: pass
                    if not os.path.isfile(directory + 'p' + show['ratingKey'] + '.jpg'):
                        try:r = session.get(image_url.format(
                            self.ssl, self.host, self.port, poster, self.token)).content
                            open(directory + 'p' + show['ratingKey'] + '.jpg', 'wb').write(r)
                        except: continue

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(time.time() + 86400 * offset, tz=zone))
