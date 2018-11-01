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

__version__ = '0.0.1'

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
        'http://{0}:{1}/library/sections/1/recentlyAdded?X-Plex-Token={2}&X-Plex-Container-Start=0&X-Plex-Container-Size={3}'
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
        """Return the state attributes of the sensor."""
        data = []
        attributes = {}
        default = {}
        default['title_default'] = '$title'
        default['line1_default'] = '$episode'
        default['line2_default'] = '$release'
        default['line3_default'] = '$rating - $runtime'
        default['line4_default'] = '$number - $studio'
        default['icon'] = 'mdi:eye-off'
        data.append(default)
        for show in self.data:
            pre = {}
            self.attribNum += 1
            if 'studio' in show:
                pre['title'] = show.get('title', '')
                pre['episode'] = ''
            else:
                pre['title'] = show.get('grandparentTitle', '')
                pre['episode'] = show.get('title', '')
            try:
                if 'viewCount' in show: pre['flag'] = False
                else: pre['flag'] = True
            except: pre['flag'] = False
            if show.get('rating', 0) > 0:
                pre['rating'] = '\N{BLACK STAR}' + str(show.get('rating', ''))
            else:
                pre['rating'] = ''
            pre['number'] = ('S{:02d}E{:02d}').format(show.get('parentIndex', ''), show.get('index', ''))
            pre['airdate'] = datetime.utcfromtimestamp(show.get('addedAt')).isoformat() + 'Z'
            if math.floor(show.get('duration') / 60000) > 0:
                pre['runtime'] = math.floor(show.get('duration') / 60000)
            pre['release'] = '$day, $date $time'
            try:
                pre['poster'] = '../local/custom-lovelace/upcoming-media-card/images/plex/p' + show['ratingKey'] + '.jpg'
            except:
                pre['poster'] = ''
            try:
                pre['fanart'] = '../local/custom-lovelace/upcoming-media-card/images/plex/f' + show['ratingKey'] + '.jpg'
            except:
                pre['fanart'] = ''
            data.append(pre)

        attributes['data'] = json.dumps(data)
        return attributes

    def update(self):
        """Update the data for the sensor."""
        try:
            res = requests.get(
                ENDPOINTS[self.type].format(
                    self.host, self.port,
                    self.token, self.items),
                headers={ 'Accept': 'application/json' },
                timeout=10)
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return
        
        if res.status_code == 200:
            self.data = res.json()['MediaContainer']['Metadata']
            self._state = self.attribNum

        directory = 'www/custom-lovelace/upcoming-media-card/images/plex/'
        if not os.path.exists(directory): os.makedirs(directory)

        media_ids = []
        for show in self.data: media_ids.append(show['ratingKey'])

        """Get imgs for shown media, delete imgs for media no longer in list"""
        if not set(media_ids).issubset(os.listdir(directory)):
            for filename in os.listdir(directory):
                if str(media_ids).find(filename[1:-4]) == -1: 
                    os.remove(directory + filename)
            for show in self.data:
                if not os.path.isfile(directory + 'p' + show['ratingKey'] + '.jpg'):
                    try:
                        imgurl = BytesIO(requests.get('http://{0}:{1}{2}?X-Plex-Token={3}'.format(
                            self.host, self.port, show.get('parentThumb'), self.token)).content)
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
