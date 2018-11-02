"""
Plex component for the Upcoming Media Lovelace card.

"""
import logging, time, re, os, os.path, json, math, requests
from datetime import date, datetime
from PIL import Image
from io import BytesIO
import voluptuous as vol, homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_MONITORED_CONDITIONS
from homeassistant.helpers.entity import Entity

__version__ = '0.0.3'

_LOGGER = logging.getLogger(__name__)

CONF_ITEMS = 'item_count'
CONF_TOKEN = 'token'


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 32400
DEFAULT_ITEMS = '5'

SENSOR_TYPES = {
    'media': ['media', None, None]
}

ENDPOINTS = {
    'media':
        'http://{0}:{1}/library/sections/{2}/recentlyAdded?X-Plex-Token={3}&X-Plex-Container-Start=0&X-Plex-Container-Size={4}'
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_ITEMS, default=DEFAULT_ITEMS): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=['media']):
        vol.All(cv.ensure_list, [vol.In(list(SENSOR_TYPES))]),
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Plex platform."""
    conditions = config.get(CONF_MONITORED_CONDITIONS)
    add_devices([Plex_RecentSensor(hass, config, sensor) for sensor in conditions], True)

class Plex_RecentSensor(Entity):
    """Implementation of the Plex sensor."""

    def __init__(self, hass, conf, sensor_type):
        """Create Plex entity."""
        from pytz import timezone
        self.conf = conf
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.token = conf.get(CONF_TOKEN)
        self.items = int(conf.get(CONF_ITEMS))
        self._state = None
        self.data = []
        self._tz = timezone(str(hass.config.time_zone))
        self.type = sensor_type
        self._name = SENSOR_TYPES[self.type][0]
        self.attribNum = 0
        self.now = str(get_date(self._tz))
        self.sections = []

    @property
    def name(self):
        """Return the name of the sensor."""
        return ('{} {}').format('Plex_Recent', self._name)

    @property
    def state(self):
        """Return sensor state."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return JSON for the sensor."""
        data = []
        attributes = {}
        default = {}
        self.attribNum = 0
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
                pre['number'] = ('S{:02d}E{:02d}').format(show.get('parentIndex', ''), show.get('index', ''))
            else: continue
            if 'viewCount' in show: pre['flag'] = False
            else: pre['flag'] = True
            if show.get('rating', 0) > 0: pre['rating'] = '\N{BLACK STAR}' + str(show['rating'])
            else: pre['rating'] = ''
            pre['airdate'] = datetime.utcfromtimestamp(show.get('addedAt')).isoformat() + 'Z'
            if show.get('duration', 0) > 0: pre['runtime'] = math.floor(show['duration'] / 60000)
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
        """Update the data for the sensor."""
        try:
            self.sections = []
            getsec = requests.get('http://{0}:{1}/library/sections/all/?X-Plex-Token={2}'.format(
                    self.host, self.port, self.token),
                headers={ 'Accept': 'application/json' },
                timeout=10)
            for key in getsec.json()['MediaContainer']['Directory']:
                self.sections.append(key['key'])

        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return
        
        if getsec.status_code == 200:
            self.data = []
            for key in self.sections:
                res = requests.get(
                    ENDPOINTS[self.type].format(
                        self.host, self.port, key,
                        self.token, self.items),
                    headers={ 'Accept': 'application/json' },
                    timeout=10)
                self.data += res.json()['MediaContainer']['Metadata']

        directory = 'www/custom-lovelace/upcoming-media-card/images/plex/'
        if not os.path.exists(directory): os.makedirs(directory)

        media_ids = []
        self.data = sorted(self.data, key = lambda i: i['addedAt'], reverse=True)
        for show in self.data[:self.items]:
            media_ids.append(show['ratingKey'])

        """Get imgs for shown media, delete imgs for media no longer in list"""
        if not set(media_ids).issubset(os.listdir(directory)):
            for filename in os.listdir(directory):
                if filename.endswith('.jpg') and str(media_ids).find(filename[1:-4]) == -1: 
                    os.remove(directory + filename)

            for show in self.data[:self.items]:
                if show.get('type') == 'movie': poster = show.get('thumb')
                elif show.get('type') == 'episode': poster = show.get('parentThumb')
                else: continue
                if not os.path.isfile(directory + 'p' + show['ratingKey'] + '.jpg'):
                    try:
                        imgurl = BytesIO(requests.get('http://{0}:{1}{2}?X-Plex-Token={3}'.format(
                            self.host, self.port, poster, self.token)).content)
                        img = Image.open(imgurl)
                        img.resize((150, 225), Image.ANTIALIAS).save(
                            directory + 'p' + show['ratingKey'] + '.jpg', 'JPEG')
                    except: pass
                if not os.path.isfile(directory + 'f' + show['ratingKey'] + '.jpg'):
                    try:
                        imgurl = BytesIO(requests.get('http://{0}:{1}{2}?X-Plex-Token={3}'.format(
                            self.host, self.port, show.get('art'), self.token)).content)
                        img = Image.open(imgurl)
                        img = img.resize((300, 168), Image.ANTIALIAS).save(
                            directory + 'f' + show['ratingKey'] + '.jpg', 'JPEG')
                    except: pass

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    day = 60 * 60 * 24
    return datetime.date(datetime.fromtimestamp(time.time() + day * offset, tz=zone))
