import requests
import constants
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import re
from dataclasses import dataclass

@dataclass
class Flightplan:
    flight_rules: str
    aircraft: str
    aircraft_faa: str
    aircraft_short: str
    departure: str
    arrival: str
    alternate: str
    cruise_tas: int
    altitude: int
    deptime: datetime
    enroute_time: timedelta
    fuel_time: timedelta
    remarks: str
    route: str
    revision_id: int
    assigned_transponder: str

@dataclass
class Server:
    ident: str
    hostname_or_ip: str
    location: str
    name: str
    clients_connection_allowed: bool
    client_connections_allowed: bool
    is_sweatbox: bool

@dataclass
class Pilot:
    cid: int
    name: str
    callsign: str
    server: Server
    pilot_rating: int
    latitude: float
    longitude: float
    altitude: int
    groundspeed: int
    transponder: str
    heading: int
    qnh_i_hg: float
    qnh_mb: int
    flightplan: Flightplan
    logon_time: datetime
    last_updated: datetime

@dataclass
class PilotRating:
    id: int
    short_name: str
    long_name: str

@dataclass
class Rating:
    id: int
    short_name: str
    long_name: str

@dataclass
class Metar:
    field: str
    time: datetime
    condition: str
    raw_text: str


class TTLCache():
    def __init__(self, ttl):
        self.ttl = ttl
        self._cache = {}
        self._last_update_time = {}

    def is_stale(self, key='_ALL'):
        now = datetime.now(timezone.utc)
        if key not in self._cache:
            return True
        else:
            return self._cache[key] == None or (now - self._last_update_time[key]).total_seconds() > self.ttl
    
    def get_cached(self, key='_ALL'):
        return self._cache[key] # should probably add logic checks for stale data here
    
    def cache(self, val, key='_ALL'):
        self._cache[key] = val
        self._last_update_time[key] = datetime.now(timezone.utc)


class VatsimStatus():

    def __init__(self, status_url=constants.STATUS_JSON_URL):

        try:
            r = requests.get(status_url)
        except Exception as e:
            raise
        
        j = r.json()
        self.status_json_url = status_url
        self.data_json_url = j['data']['v3'][0]
        self.transceivers_json_url = j['data']['transceivers'][0]
        self.servers_json_url = j['data']['servers'][0]
        self.servers_sweatbox_json_url = j['data']['servers_sweatbox'][0]
        self.user_php_url = j['user'][0]
        self.metar_php_url = j['metar'][0]


class VatsimDataAPI():

    def __init__(self, vatsim_status=None, DATA_TTL=15, METAR_TTL=60):  # change timeouts to be configurable here
        if vatsim_status is None:
            self.vatsim_status = VatsimStatus()
        else:
            assert isinstance(vatsim_status, VatsimStatus)
            self.vatsim_status = vatsim_status

        self._metar_cache = TTLCache(METAR_TTL)
        self._data_cache  = TTLCache(DATA_TTL)

    def _parse_metar(self, raw_text):
        r = re.compile(r'(?P<field>[\S]+?) (?P<time>[0-9]{6}Z?) (?P<condition>.*)')
        try:
            m = r.match(raw_text)
            today = datetime.now(timezone.utc).today()
            args = {
                'field'     : m.group('field'),
                'condition' : m.group('condition'),
                'raw_text'  : raw_text,
                'time'      : datetime(today.year, today.month, int(m.group('time')[:2]), int(m.group('time')[2:4]), int(m.group('time')[4:6]))
            }
            
        except:
            args = {
                'field'     : raw_text[:4],
                'condition' : None,
                'raw_text'  : raw_text,
                'time'      : None
            }
        return Metar(**args)

    def _fetch_metars(self, fields):
        if isinstance(fields, str):
            field_str = fields
        else:
            field_str = ','.join(fields)
        url = self.vatsim_status.metar_php_url + '?' + urlencode({'id': field_str})
        print(url)
        try:
            r = requests.get(url)
        except Exception as e:
            raise
        metars = {}
        for row in r.text.splitlines():
            metar = self._parse_metar(row)
            metars[metar.field] = metar

        return metars

    def metars(self, fields=None, force=False):

        if fields is None:
            if force or self._metar_cache.is_stale():

                new_metars = self._fetch_metars('all')
                self._metar_cache.cache(new_metars)
                return new_metars
            else:
                # print('cache alive')
                return self._metar_cache.get_cached()
        else:
            pass # TODO: handle list of fields. Need to construc the fresh list and the stale list separately then fetch as needed


    def metar(self, field, force=False):
        if force or self._metar_cache.is_stale(field):

            metar = self._fetch_metars(field)
            self._metar_cache.cache(metar, field)
            return metar
        else:
            # print('cache alive')
            # print(self._metar_cache._last_update_time)
            return self._metar_cache.get_cached(field)

    def pilot(self, cid=None, callsign=None):
        pass

    def pilots(self, cid=None, callsigns=None):
        pass

    def controller(self):
        pass

    def controllers(self):
        pass

    def atises(self):
        pass

    def atis(self):
        pass

    # all, active only, or prefile only
    def flight_plans(self):
        pass


# if __name__ == '__main__':

api = VatsimDataAPI()
m = api.metars()
n = api.metars()
k = api.metar('KSFO')
n = api.metar('KSFO')
print(k)

# r = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
# x = r.json()['pilots'][0]['flight_plan']
# print(x)
# y = Flightplan(**x)
# print(y)
# print(y.remarks)